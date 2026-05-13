from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .novel import NovelChapter, NovelPlan


class ExtractedProductionAsset(BaseModel):
    """A reusable production asset extracted for one episode."""

    id: str
    name: str
    type: str
    description: str = ""
    continuity_lock: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedStoryboardFrame(BaseModel):
    """A storyboard-ready visual beat for one episode."""

    frame_id: str
    order: int
    scene_ref: str
    character_refs: List[str] = Field(default_factory=list)
    prop_refs: List[str] = Field(default_factory=list)
    costume_refs: List[str] = Field(default_factory=list)
    special_effect_refs: List[str] = Field(default_factory=list)
    action_description: str
    camera_angle: str = "平视"
    camera_movement: str = "缓慢推镜"
    visual_atmosphere: str = "电影级写实光影，连续镜头语境"
    dialogue: str = ""
    image_prompt: str = ""
    video_prompt: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EpisodeProductionPackage(BaseModel):
    """A complete per-episode package for Studio persistence and QA."""

    episode_id: str
    order: int
    title: str
    summary: str
    script_text: str
    storyboard_frames: List[ExtractedStoryboardFrame] = Field(default_factory=list)
    characters: List[ExtractedProductionAsset] = Field(default_factory=list)
    scenes: List[ExtractedProductionAsset] = Field(default_factory=list)
    props: List[ExtractedProductionAsset] = Field(default_factory=list)
    costumes: List[ExtractedProductionAsset] = Field(default_factory=list)
    special_effects: List[ExtractedProductionAsset] = Field(default_factory=list)
    continuity_locks: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EpisodeProductionExtractor:
    """Deterministically extract shootable episode packages from a NovelPlan."""

    _PROP_KEYWORDS = {
        "phone": "手机",
        "call": "手机",
        "signal": "信号装置",
        "contract": "合同",
        "wedding": "婚戒",
        "bride": "婚戒",
        "bag": "包",
        "delivery": "配送箱",
        "key": "钥匙",
        "letter": "信件",
        "crystal": "晶体",
        "proof": "证据袋",
        "evidence": "证据袋",
    }
    _EFFECT_KEYWORDS = {
        "ghost": "灵异冷雾",
        "dead": "异常来电光效",
        "rain": "雨幕",
        "magic": "能量粒子",
        "dream": "梦境柔焦",
        "future": "全息噪点",
        "fire": "火光烟雾",
        "explosion": "冲击波",
        "secret": "阴影遮罩",
        "mystery": "悬疑暗角",
    }
    _CAMERA_PATTERN = ("低角度", "平视", "俯视", "侧逆光")
    _MOVEMENT_PATTERN = ("缓慢推镜", "静止观察", "横移跟拍", "快速切近")

    def extract(self, plan: NovelPlan) -> List[EpisodeProductionPackage]:
        """Extract packages for all chapters in a novel plan."""
        characters = self._build_character_assets(plan)
        packages = []
        for chapter in plan.chapters:
            packages.append(self._extract_chapter(plan, chapter, characters))
        return packages

    def _extract_chapter(
        self,
        plan: NovelPlan,
        chapter: NovelChapter,
        characters: List[ExtractedProductionAsset],
    ) -> EpisodeProductionPackage:
        """Extract all production atoms for one chapter."""
        source_text = " ".join(
            part for part in [chapter.summary, chapter.prose, chapter.cliffhanger] if part
        )
        scenes = [self._build_scene_asset(plan, chapter)]
        props = self._build_prop_assets(source_text, chapter.order)
        costumes = self._build_costume_assets(plan, chapter.order, characters)
        effects = self._build_effect_assets(plan, source_text, chapter.order)
        script_text = self._chapter_script(plan, chapter, characters, props, costumes)
        frames = self._build_frames(
            chapter=chapter,
            characters=characters,
            scenes=scenes,
            props=props,
            costumes=costumes,
            effects=effects,
        )
        locks = {
            "characters": {asset.id: asset.continuity_lock for asset in characters},
            "scenes": {asset.id: asset.continuity_lock for asset in scenes},
            "props": {asset.id: asset.continuity_lock for asset in props},
            "costumes": {asset.id: asset.continuity_lock for asset in costumes},
            "special_effects": {asset.id: asset.continuity_lock for asset in effects},
        }
        return EpisodeProductionPackage(
            episode_id=chapter.chapter_id,
            order=chapter.order,
            title=chapter.title,
            summary=chapter.summary,
            script_text=script_text,
            storyboard_frames=frames,
            characters=characters,
            scenes=scenes,
            props=props,
            costumes=costumes,
            special_effects=effects,
            continuity_locks=locks,
            metadata={
                "extractor": "episode_production_extractor.v1",
                "source_chapter_id": chapter.chapter_id,
                "arc": chapter.metadata.get("arc"),
            },
        )

    def _build_character_assets(self, plan: NovelPlan) -> List[ExtractedProductionAsset]:
        """Create stable character description assets from the relationship graph."""
        raw_characters = plan.relationship_graph.get("characters") or ["Protagonist"]
        assets = []
        for index, name in enumerate(raw_characters[:8], start=1):
            role = "主角" if index == 1 else "关键对手/关系角色"
            assets.append(
                ExtractedProductionAsset(
                    id=self._slug(f"char_{name}"),
                    name=name,
                    type="character",
                    description=(
                        f"{name}，{role}。视觉方向：{plan.world_bible.get('visual_style', 'cinematic')}；"
                        f"核心冲突关联：{plan.world_bible.get('core_conflict', plan.premise)}"
                    ),
                    continuity_lock="face, hairstyle, silhouette, signature outfit, voice",
                    metadata={"relationship_role": role},
                )
            )
        return assets

    def _build_scene_asset(self, plan: NovelPlan, chapter: NovelChapter) -> ExtractedProductionAsset:
        """Infer one editable scene asset for an episode."""
        genre = plan.world_bible.get("genre", "character-driven drama")
        scene_name = self._scene_name_for(genre, chapter)
        return ExtractedProductionAsset(
            id=self._slug(f"scene_{chapter.order}_{scene_name}"),
            name=scene_name,
            type="scene",
            description=f"{scene_name}，{genre} 氛围，围绕本集弧线 {chapter.metadata.get('arc', '')} 设计。",
            continuity_lock="location layout, time of day, dominant lighting, color temperature",
            metadata={"genre": genre, "chapter_order": chapter.order},
        )

    def _build_prop_assets(self, text: str, chapter_order: int) -> List[ExtractedProductionAsset]:
        """Infer signature props from source keywords with a fallback hero prop."""
        lowered = text.lower()
        names = []
        for token, label in self._PROP_KEYWORDS.items():
            if token in lowered and label not in names:
                names.append(label)
        if not names:
            names.append("关键线索物")
        return [
            ExtractedProductionAsset(
                id=self._slug(f"prop_{chapter_order}_{name}"),
                name=name,
                type="prop",
                description=f"{name}，本集推动剧情的信息载体，需在分镜和视频中保持外观一致。",
                continuity_lock="shape, material, mark, screen/text state",
                metadata={"chapter_order": chapter_order},
            )
            for name in names[:4]
        ]

    def _build_costume_assets(
        self,
        plan: NovelPlan,
        chapter_order: int,
        characters: List[ExtractedProductionAsset],
    ) -> List[ExtractedProductionAsset]:
        """Create default locked costume assets for visible characters."""
        genre = plan.world_bible.get("genre", "drama")
        assets = []
        for character in characters[:3]:
            costume_name = f"{character.name} 本集主服装"
            assets.append(
                ExtractedProductionAsset(
                    id=self._slug(f"costume_{chapter_order}_{character.name}"),
                    name=costume_name,
                    type="costume",
                    description=f"{costume_name}，符合 {genre}，颜色和轮廓服务角色识别。",
                    continuity_lock="palette, silhouette, fabric, accessories",
                    metadata={"character_id": character.id, "chapter_order": chapter_order},
                )
            )
        return assets

    def _build_effect_assets(
        self,
        plan: NovelPlan,
        text: str,
        chapter_order: int,
    ) -> List[ExtractedProductionAsset]:
        """Extract visual effects and always provide one atmosphere effect."""
        lowered = f"{text} {plan.premise}".lower()
        names = []
        for token, label in self._EFFECT_KEYWORDS.items():
            if token in lowered and label not in names:
                names.append(label)
        names.append("统一电影颗粒与边缘光")
        return [
            ExtractedProductionAsset(
                id=self._slug(f"fx_{chapter_order}_{name}"),
                name=name,
                type="special_effect",
                description=f"{name}，作为本集可复用的视觉特效提示，避免每镜随机漂移。",
                continuity_lock="intensity, color, screen position, timing",
                metadata={"chapter_order": chapter_order},
            )
            for name in names[:4]
        ]

    def _chapter_script(
        self,
        plan: NovelPlan,
        chapter: NovelChapter,
        characters: List[ExtractedProductionAsset],
        props: List[ExtractedProductionAsset],
        costumes: List[ExtractedProductionAsset],
    ) -> str:
        """Compile an episode script that keeps Film Core asset tags visible."""
        protagonist = characters[0].name if characters else "Protagonist"
        prop_tags = " ".join(f"[prop={asset.id}]" for asset in props)
        costume_tags = " ".join(f"[costume={asset.id}]" for asset in costumes[:1])
        return "\n".join(
            [
                f"INT. EP{chapter.order:02d} CONTINUITY SPACE",
                f"{protagonist}: {chapter.summary}",
                f"△ {chapter.prose} {prop_tags} {costume_tags}".strip(),
                f"Narrator: {chapter.cliffhanger}",
            ]
        )

    def _build_frames(
        self,
        *,
        chapter: NovelChapter,
        characters: List[ExtractedProductionAsset],
        scenes: List[ExtractedProductionAsset],
        props: List[ExtractedProductionAsset],
        costumes: List[ExtractedProductionAsset],
        effects: List[ExtractedProductionAsset],
    ) -> List[ExtractedStoryboardFrame]:
        """Build three editable frames for hook, development and cliffhanger."""
        scene = scenes[0]
        character_ids = [asset.id for asset in characters[:2]]
        prop_ids = [asset.id for asset in props[:2]]
        costume_ids = [asset.id for asset in costumes[:2]]
        effect_ids = [asset.id for asset in effects[:2]]
        frame_sources = [
            ("hook", chapter.summary),
            ("development", chapter.prose),
            ("cliffhanger", chapter.cliffhanger),
        ]
        frames = []
        for index, (role, text) in enumerate(frame_sources, start=1):
            action = self._compact(text, 180)
            atmosphere = f"{scene.name}，{effects[0].name if effects else '电影级光影'}，{chapter.metadata.get('arc', 'drama')} 节奏"
            prompt_parts = [atmosphere, action, self._CAMERA_PATTERN[(index - 1) % len(self._CAMERA_PATTERN)]]
            frames.append(
                ExtractedStoryboardFrame(
                    frame_id=f"{chapter.chapter_id}_frame_{index:02d}",
                    order=index,
                    scene_ref=scene.id,
                    character_refs=character_ids,
                    prop_refs=prop_ids,
                    costume_refs=costume_ids,
                    special_effect_refs=effect_ids,
                    action_description=action,
                    camera_angle=self._CAMERA_PATTERN[(index - 1) % len(self._CAMERA_PATTERN)],
                    camera_movement=self._MOVEMENT_PATTERN[(index - 1) % len(self._MOVEMENT_PATTERN)],
                    visual_atmosphere=atmosphere,
                    dialogue=action if role == "hook" else "",
                    image_prompt="，".join(part for part in prompt_parts if part),
                    video_prompt=f"{action}；{self._MOVEMENT_PATTERN[(index - 1) % len(self._MOVEMENT_PATTERN)]}",
                    metadata={"story_role": role},
                )
            )
        return frames

    def _scene_name_for(self, genre: str, chapter: NovelChapter) -> str:
        """Pick an understandable default scene name from genre and chapter arc."""
        lowered = genre.lower()
        if "suspense" in lowered:
            return "夜间调查现场"
        if "romance" in lowered:
            return "都市情感冲突空间"
        if "fantasy" in lowered:
            return "现实与异象交界处"
        return f"第{chapter.order}集核心场景"

    def _slug(self, value: str) -> str:
        """Create stable ids while preserving Chinese names when present."""
        cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "_", value.strip().lower())
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        return cleaned or "asset"

    def _compact(self, value: str, limit: int) -> str:
        """Compact generated prose for storyboard fields."""
        text = " ".join((value or "").split())
        return text[:limit].rstrip() + ("..." if len(text) > limit else "")
