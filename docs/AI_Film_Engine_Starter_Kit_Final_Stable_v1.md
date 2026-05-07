# AI Film Engine Starter Kit Final Stable v1

> 最终稳定版（不要再频繁修改）

## 项目目标

构建工业级 AI 漫剧 / AI 电影引擎。

不是：

- AI 视频 Demo
- Prompt 拼接器
- 简单工作流网站

而是：

- AI 内容工厂
- AI Film Engine
- 长剧情一致性系统
- 角色一致性系统
- 自动 QA + Retry 系统

---

# 最终推荐架构

```text
Jellyfish
    ↓
Film Core
    ↓
Director DSL
    ↓
Shot Graph
    ↓
Prompt Compiler
    ↓
Runtime Adapter
    ↓
Kling / Seedance / Veo
    ↓
QA Engine
    ↓
Retry Engine
```

---

# 主基座（最终推荐）

## Jellyfish

GitHub:
https://github.com/Forget-C/Jellyfish

定位：

- AI Studio OS
- Workflow Core
- Project System
- Asset Management
- Async Task System
- Shot Management
- Studio UI

建议：

- Fork 后二次开发
- 保留 workflow/studio 架构
- 在其上扩展 Film Core

---

# 从哪些项目拆什么

## 1. huobao-drama

GitHub:
https://github.com/chatfire-AI/huobao-drama

拆：

- render pipeline
- ffmpeg orchestration
- subtitle pipeline
- TTS workflow
- stitching logic
- runtime adapters

最终定位：

# Runtime Layer

---

## 2. director_ai

GitHub:
https://github.com/freestylefly/director_ai

拆：

- Director DSL
- Shot abstraction
- Camera grammar
- Scene timeline
- Transition system
- Shot metadata

最终定位：

# Director Layer

---

## 3. BigBanana-AI-Director

GitHub:
https://github.com/shuyu-labs/BigBanana-AI-Director

拆：

- emotion-camera mapping
- pacing rules
- cinematic rhythm
- composition heuristics

最终定位：

# Cinematic Rule Layer

---

## 4. waoowaoo

GitHub:
https://github.com/waooAI/waoowaoo

拆：

- workflow graph
- orchestration
- context memory
- agent coordination

最终定位：

# Orchestration Layer

---

## 5. Toonflow-app

GitHub:
https://github.com/HBAI-Ltd/Toonflow-app

拆：

- storyboard UI
- timeline UI
- shot editing interaction

最终定位：

# Storyboard Layer

---

## 6. StoryDiffusion

GitHub:
https://github.com/HVision-NKU/StoryDiffusion

拆：

- character consistency
- reference image pipeline
- long-story continuity

最终定位：

# Character Consistency Layer

---

# 必须自己研发（真正壁垒）

## 1. Film State Engine

维护：

- character continuity
- outfit continuity
- lighting continuity
- emotional continuity
- timeline continuity

这是下一代 AI Film Engine 最大壁垒。

---

## 2. QA Engine

自动检测：

- 崩脸
- 多手指
- outfit drift
- lighting mismatch
- shot continuity failure

---

## 3. Retry Engine

工作流：

```text
Generate
→ QA
→ Repair
→ Retry
→ Re-QA
```

---

## 4. Prompt Compiler

将：

- Director DSL
- Character State
- Scene State
- Shot State

编译为：

- Kling prompt
- Seedance prompt
- Veo prompt

---

## 5. Character Bible

包括：

```yaml
character:
  id: heroine_001
  lora: heroine_v12
  outfit:
    school_uniform
  hairstyle:
    black_long
```

---

## 6. Scene Bible

包括：

- lighting
- weather
- color tone
- camera style
- time of day

---

# 推荐目录结构

```text
ai-film-engine/
│
├── backend/
├── runtime/
├── skills/
├── tests/
├── freeze/
├── samples/
├── benchmarks/
├── schemas/
├── tasks/
└── docs/
```

---

# Skill 固定结构

每个 Skill 必须：

```text
开发
→ 测试
→ Freeze
→ Sample
→ Benchmark
```

目录：

```text
skills/
tests/
freeze/
samples/
benchmarks/
```

---

# Director DSL Sample

```yaml
scene:
  mood: suspense
  pacing: slow

shots:
  - framing: medium_closeup
    movement: dolly_in
    lens: 85mm
    emotion: tension
```

---

# Shot Graph Samples

## confession_sequence.yaml

```yaml
sequence_id: confession_scene_v1

scene:
  location: rooftop_night
  mood: emotional

shots:
  - id: shot_001
    type: establishing_wide

  - id: shot_002
    type: medium_two_shot

  - id: shot_003
    type: closeup
    emotion: emotional
```

---

## fight_sequence.yaml

```yaml
sequence_id: alley_fight_v1

scene:
  location: rainy_alley
  mood: aggressive

shots:
  - id: shot_001
    type: handheld_wide

  - id: shot_002
    type: impact_closeup

  - id: shot_003
    type: tracking_shot
```

---

## suspense_sequence.yaml

```yaml
sequence_id: suspense_corridor_v1

scene:
  location: dark_corridor
  mood: suspense

shots:
  - id: shot_001
    type: hallway_wide

  - id: shot_002
    type: over_shoulder

  - id: shot_003
    type: reveal_shot
```

---

# 最终开发顺序（固定）

```text
1. Runtime
2. Director DSL
3. Shot Graph
4. Prompt Compiler
5. Character Registry
6. Scene Registry
7. QA Engine
8. Retry Engine
9. Film State Engine
```

---

# 真正行业结论

未来真正值钱的：

不是：

# “视频模型”

而是：

# “稳定、低成本、批量生产高一致性内容的能力”

真正壁垒：

- Director DSL
- Shot Graph
- Character Registry
- Film State Engine
- QA Engine
- Retry Engine

目标：

# AI 内容工厂
