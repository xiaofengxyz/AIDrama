from src.film_engine import EpisodeProductionExtractor, NovelEngine


def test_episode_production_extractor_builds_per_episode_packages():
    """Each generated chapter should expose script, storyboard, assets and locks."""
    plan = NovelEngine().expand(
        "Maya: The dead customer's phone rings again. The secret signal points to a hidden proof.",
        title="Night Signal",
        target_chapters=2,
    )

    packages = EpisodeProductionExtractor().extract(plan)

    assert len(packages) == 2
    assert packages[0].script_text.startswith("INT. EP01")
    assert "[prop=" in packages[0].script_text
    assert "[costume=" in packages[0].script_text
    assert len(packages[0].storyboard_frames) == 3
    assert packages[0].characters[0].continuity_lock
    assert packages[0].props
    assert packages[0].costumes
    assert packages[0].special_effects
    assert packages[0].continuity_locks["characters"]


def test_episode_production_packages_keep_frame_asset_references():
    """Storyboard frames should reference extracted characters, props, costumes and effects."""
    plan = NovelEngine().expand(
        "Jun: The courier opens a delivery bag in the rain and finds a contract.",
        title="Delivery Contract",
        target_chapters=1,
    )

    package = EpisodeProductionExtractor().extract(plan)[0]
    frame = package.storyboard_frames[0]

    assert frame.character_refs
    assert frame.prop_refs
    assert frame.costume_refs
    assert frame.special_effect_refs
    assert frame.image_prompt
    assert frame.video_prompt
