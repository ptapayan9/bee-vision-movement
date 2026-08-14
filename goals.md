# Bee Vision Movement Roadmap

This is the canonical build plan for the project. Read this file at the start
of a new session, work on the first incomplete milestone, and update its
checkboxes only after the acceptance checks pass.

Last reviewed: 2026-08-13

## Current handoff

- Current milestone: Milestone 2 — person-mask prototype.
- Next task: add and test a pure confidence-to-binary-mask helper, then connect
  it and the tested BGR-to-RGB conversion helper inside
  `PersonSegmenter.apply(frame)`.
- Current blocker: none. Live testing proved that MOG2 detects a moving person
  but gradually absorbs a motionless person into the background, so the
  pretrained person-segmentation objective is now approved.
- Checkpoint: MediaPipe 1.0.0 is a direct dependency; the official 244 KB
  SelfieSegmenter landscape model is stored under `src/bvm/models` and loads
  successfully. `PersonSegmenter` initializes the model alongside the existing
  `ForegroundSegmenter`. The BGR-to-RGB helper has a passing unit test, but
  `PersonSegmenter.apply(frame)` and confidence-mask conversion are not yet
  implemented. The existing segmentation tests and Pyright pass.
- Collaboration rule: the user writes all implementation and test code. Codex
  should guide, explain, review, and suggest verification commands. Codex may
  edit roadmap or documentation files only when explicitly requested.

## Product goal

Create a real-time, bee-inspired camera experience. When a person enters the
camera frame, the normal image is transformed into a recognizable body
silhouette composed of many small, bright dots against a dark background.
The person mask must be based on semantic person recognition so the silhouette
remains visible when the person stops moving.

The first release is an artistic effect inspired by the supplied visual
reference. It is not intended to be a scientifically exact simulation of how
bee compound eyes perceive humans.

## Initial assumptions

- The application runs locally on macOS as a Python desktop program.
- The first version supports one connected camera and one person.
- The camera remains stationary while the effect is running.
- Processing happens locally; camera frames are not saved by default.
- The first useful version favors a clear, stable effect over advanced visual
  accuracy.
- Provisional performance target: at least 20 displayed frames per second at
  720p on the development machine. Measure this before optimizing.
- Add a library as a direct dependency only when project code imports it for a
  verified milestone. Do not install learning tools speculatively.

## Non-goals for the first release

- Scientifically validated bee-vision simulation
- Multiple-person identity tracking
- Body-joint or pose estimation
- Cloud processing, accounts, databases, or remote APIs
- Mobile or browser deployment
- Automatic recording or collection of camera footage
- Training a custom machine-learning model

## Minimal architecture

Keep the application as one local process with one frame-processing loop:

```text
Camera or video source
        ↓
      Frame
        ↓
 Person/foreground mask
        ↓
 Stable dot renderer
        ↓
   Preview window
```

### Module responsibilities

| Module | Responsibility |
| --- | --- |
| `capture/camera.py` | Open a camera and provide frames safely. |
| `capture/video.py` | Provide frames from a saved video for repeatable testing. |
| `core/frames.py` | Define shared NumPy frame and mask contracts when multiple stages need them. |
| `vision/segmentation.py` | Convert a frame into a person/foreground mask. |
| `visualization/overlays.py` | Turn a frame and mask into the dotted silhouette. |
| `visualization/plots.py` | Create offline Matplotlib diagnostic plots after metrics exist. |
| `data/datasets.py` | Convert recorded scalar metrics into pandas tables for offline analysis. |
| `pipelines/analyze_video.py` | Run the stages in order without owning their internal logic. |
| `main.py` | Parse user options, select the input source, and start the pipeline. |
| `config/settings.py` | Hold visual settings only after real settings are needed. |
| `utils/logging.py` | Provide small startup, shutdown, timing, and error logs when needed. |

The existing `tracking`, `movement`, and `data` packages are not required for
the first release. Leave them empty until a verified requirement needs them.

## Build milestones

### Milestone 0 — project foundation

- [x] Create the Python 3.12 `src/bvm` package scaffold.
- [x] Configure `uv`, Hatchling, Ruff, Pyright, Pytest, and CI.
- [x] Add the initial CLI and video-path validation tests.
- [x] Document local development and the project goal.
- [x] Create this implementation roadmap.

Acceptance check:

- [x] Existing unit tests, Ruff checks, and Pyright checks pass.

### Milestone 1 — reliable live camera preview

Purpose: prove that the application can acquire and display live frames before
adding image-processing complexity.

- [x] Add `opencv-python` as a runtime dependency with `uv add`.
- [x] Implement camera opening in `capture/camera.py` with camera index `0` as
  the default.
- [x] Detect and clearly report failure to open the camera.
- [x] Read and display frames continuously.
- [x] Allow the user to quit with a simple key such as `q`.
- [x] Release the camera and destroy preview windows on every exit path.
- [x] Confirm camera index `0` is the intended camera; indices `1` and `2` were
  not needed.
- [x] Confirm macOS camera permission for the terminal or IDE being used.

Acceptance checks:

- [x] A live, unfrozen preview opens from the development environment.
- [x] Closing the preview releases the camera so it can immediately reopen.
- [x] Camera-open and frame-read failures produce understandable errors.
- [x] CI and unit tests do not require physical camera hardware.

Do not change the CLI or begin segmentation until this milestone works.

### Milestone 2 — person-mask prototype

Purpose: reduce each frame to a binary decision: person/foreground or
background.

- [x] Start with OpenCV foreground subtraction because the first setup uses a
  stationary camera and a person entering the scene.
- [x] Put mask creation and cleanup in `vision/segmentation.py`.
- [x] Learn and use NumPy frame properties such as array shape, dimensions,
  data type, slicing, boolean masks, and vectorized operations.
- [x] Remove small isolated noise with minimal mask cleanup.
- [ ] Test the mask against a short repeatable video, not only the live camera.
- [x] Keep segmentation separate from display and camera handling.

Acceptance checks:

- [ ] The person is mostly white in the mask and the background is mostly black.
- [x] The mask has the same width and height as the source frame.
- [x] A unit test verifies the mask is a NumPy array with the expected shape,
  data type, and value range.
- [ ] A saved test clip produces repeatable results.

Decision gate:

- [x] Decision reached on 2026-08-08: MOG2 gradually loses a person who stands
  still and produces some background speckles. Replace only the segmentation
  stage with a pretrained person-segmentation model. Keep the working MOG2
  prototype until its replacement passes automated and live checks.

#### Pretrained person-segmentation objective

- [x] Add MediaPipe as a direct runtime dependency and obtain the official
  SelfieSegmenter landscape model from its documented source.
- [ ] Add a person segmenter alongside the MOG2 prototype rather than deleting
  working behavior first.
- [ ] Preserve the existing `apply(frame) -> mask` interface so camera capture
  and pipeline orchestration do not need redesigning.
- [ ] Convert OpenCV BGR input to the model's RGB input format.
- [ ] Convert the model's background/person categories into a binary NumPy mask
  containing only `0` and `255`.
- [ ] Add hardware-free unit tests for model input conversion, output shape,
  data type, value range, and cleanup behavior.
- [ ] Switch the live pipeline to the pretrained segmenter only after its tests
  pass.
- [ ] Verify that a person remains visible while standing still for at least 20
  seconds and record the observed background noise.
- [ ] Measure live frame rate before deciding whether model or frame-size
  optimization is necessary.
- [ ] Remove or retain the MOG2 prototype only after the replacement is
  verified.

### Milestone 3 — stable dotted-silhouette renderer

Purpose: reproduce the core look from the reference image independently of
camera and segmentation concerns.

- [ ] Make `visualization/overlays.py` accept a source frame and binary mask.
- [ ] Produce a black output image with the same dimensions as the source.
- [ ] Place dots only where the mask identifies the person.
- [ ] Begin with a fixed grid or another deterministic sampling pattern.
- [ ] Use NumPy coordinate grids and boolean-mask selection instead of a Python
  loop over every pixel, unless measurement proves a simpler loop is adequate.
- [ ] Vary dot brightness or size from source-image brightness only after the
  basic silhouette is recognizable.
- [ ] Expose only the settings proven useful, such as spacing and dot radius.

Acceptance checks:

- [ ] A synthetic person-shaped mask produces dots only inside the shape.
- [ ] The silhouette remains recognizable against a black background.
- [ ] Dots do not randomly jump or flicker when the mask is unchanged.
- [ ] Unit tests verify output dimensions, background color, and deterministic
  output.

### Milestone 4 — real-time end-to-end pipeline

Purpose: connect capture, segmentation, and rendering into one dependable
experience.

- [ ] Orchestrate the stages in `pipelines/analyze_video.py`.
- [ ] Keep acquisition, segmentation, rendering, and display as separate
  responsibilities.
- [ ] Stop cleanly if frame reading fails or the user quits.
- [ ] Measure frame-processing duration and displayed frames per second.
- [ ] Downscale frames or masks only if measurement shows performance is too
  slow.

Acceptance checks:

- [ ] Entering the frame creates a live dotted body silhouette.
- [ ] Leaving the frame returns the preview to a mostly dark background.
- [ ] The output is visually stable without obvious multi-frame lag.
- [ ] The measured frame rate meets the provisional target or the actual result
  and bottleneck are documented.
- [ ] No camera frames are written to disk unless explicitly requested.

### Milestone 5 — CLI and useful controls

Purpose: make the working pipeline repeatable without hiding it behind hardcoded
values.

- [ ] Add an explicit camera option such as `bvm --camera 0`.
- [ ] Preserve the existing saved-video input path.
- [ ] Reject conflicting camera and video inputs with a clear CLI error.
- [ ] Preserve help output when no source is selected.
- [ ] Add only proven visual controls, likely dot spacing and dot radius.
- [ ] Add CLI tests for camera selection, video selection, and conflicting input.

Acceptance checks:

- [ ] A user can intentionally run either the live camera or a saved video.
- [ ] Existing video-path validation behavior remains covered by tests.
- [ ] Invalid options fail with a clear message and nonzero exit status.

### Milestone 6 — quality, failure handling, and performance

- [ ] Unit-test segmentation and rendering with synthetic images.
- [ ] Add one integration test that processes a short sequence without opening a
  graphical window or physical camera.
- [ ] Keep hardware-dependent preview verification as a documented manual check.
- [ ] Log only startup settings, selected source, shutdown, errors, and occasional
  performance summaries—not every frame.
- [ ] Include safe fields such as operation, camera index, frame size,
  `duration_ms`, status, and error type.
- [ ] Run formatting, linting, type checking, tests, and package build.

Acceptance checks:

- [ ] CI remains deterministic and independent of camera hardware.
- [ ] Camera and processing failures leave no locked device or orphan window.
- [ ] Performance measurements identify whether capture, segmentation, or
  rendering is the slow stage.

### Learning track — NumPy, pandas, and Matplotlib

Purpose: practice these libraries through work the project genuinely needs.
NumPy supports the real-time image pipeline. pandas and Matplotlib support
offline analysis after the pipeline produces scalar measurements. None of
these goals should delay the basic dotted-silhouette experience.

#### NumPy — core image-processing tool

OpenCV frames and masks are NumPy arrays, so NumPy is part of the core design
rather than an artificial learning exercise.

- [ ] Add NumPy as a direct runtime dependency when `bvm` first imports
  `numpy`; do not rely on OpenCV's transitive dependency declaration.
- [ ] Inspect and explain frame `shape`, number of dimensions, data type, and
  channel ordering.
- [ ] Practice array slicing by selecting regions of interest.
- [ ] Practice boolean masks by selecting foreground pixels.
- [ ] Use vectorized coordinate generation and pixel selection for dot
  placement.
- [ ] Compare a vectorized operation with a small Python-loop equivalent and
  measure the difference before optimizing further.

Acceptance checks:

- [ ] Segmentation and rendering operate on documented NumPy array contracts.
- [ ] Unit tests cover representative shapes, data types, and mask boundaries.
- [ ] NumPy usage makes the frame operation clearer or faster; it is not added
  only to satisfy a library checklist.

#### pandas — gated offline metrics tool

pandas is useful only after the application produces tabular records. Keep it
out of the per-frame processing loop because constructing DataFrames on every
frame would add unnecessary latency and allocation.

- [ ] Define a small per-frame metrics record with fields such as frame number,
  timestamp, processing duration, mask area, and rendered dot count.
- [ ] Collect plain records during processing and build one pandas DataFrame
  after capture ends.
- [ ] Practice selecting columns, filtering rows, grouping, summary statistics,
  missing-value checks, and sorting on recorded metrics.
- [ ] Optionally export scalar metrics to CSV without storing raw camera frames.
- [ ] Add pandas only when the first DataFrame-backed analysis is implemented.

Acceptance checks:

- [ ] A repeatable saved-video run produces a DataFrame with documented columns
  and stable data types.
- [ ] Summary values answer a real question about performance or visual output.
- [ ] The live frame loop does not create or mutate a pandas DataFrame.

#### Matplotlib — gated diagnostics and learning plots

Matplotlib should explain recorded behavior rather than render the live effect.
OpenCV remains responsible for the real-time preview.

- [ ] Plot processing duration or frames per second over time.
- [ ] Plot mask area and rendered dot count over time to diagnose visual
  stability.
- [ ] Add labels, units, legends, titles, and readable axes.
- [ ] Save optional plots through `visualization/plots.py` for offline review.
- [ ] Add Matplotlib only when the first diagnostic plot is implemented.

Acceptance checks:

- [ ] At least one plot reveals a performance or visual-stability trend that is
  difficult to see from raw rows alone.
- [ ] Plot generation happens after processing and does not reduce live preview
  performance.
- [ ] Plot tests validate data preparation or artifact creation without relying
  on a graphical desktop.

### Milestone 7 — visual refinement

Complete these only after the plain dotted silhouette works reliably:

- [ ] Tune dot density, radius, brightness, and contrast against the reference.
- [ ] Add restrained glow or trails if they improve the effect without hiding
  the body shape.
- [ ] Consider a bee-inspired color treatment.
- [ ] Research compound-eye or bee-perception effects before labeling any
  refinement scientifically accurate.
- [ ] Upgrade segmentation only if the decision gate from Milestone 2 was met.

Acceptance checks:

- [ ] Side-by-side review shows that the result matches the intended visual
  direction.
- [ ] Refinements do not reduce the measured frame rate below the accepted
  target.
- [ ] Visual settings have useful defaults and do not require code edits.

### Milestone 8 — first release

- [ ] Document the final install and run commands in `README.md`.
- [ ] Document camera permission and camera-index troubleshooting.
- [ ] Add a short demo image, GIF, or video captured with consent.
- [ ] Verify setup from a clean environment with `uv sync --locked`.
- [ ] Run all local and CI checks.
- [ ] Tag the first usable version only after the definition of done is met.

## Failure modes and recovery

| Failure | Expected response |
| --- | --- |
| Camera cannot open | Report the index, suggest permission/index checks, and exit cleanly. |
| Frame read fails | Stop the loop, release resources, and report the failure. |
| Mask is noisy | Adjust minimal cleanup before changing technologies. |
| Person disappears when still | Evaluate semantic person segmentation at the decision gate. |
| Dots flicker | Use stable sampling; do not generate unrelated random points each frame. |
| Preview is slow | Measure each stage, then reduce resolution or optimize the measured bottleneck. |
| Window closes but camera stays busy | Fix cleanup before continuing to later milestones. |

## Definition of done for the first release

- [ ] A fresh clone installs successfully from the committed lockfile.
- [ ] The user can select a live camera from the CLI.
- [ ] A person entering the frame appears as a recognizable field of bright dots
  on a dark background.
- [ ] The effect is stable, responsive, and exits cleanly.
- [ ] Saved-video input supports repeatable development and testing.
- [ ] Automated tests cover non-hardware behavior.
- [ ] CI formatting, linting, type checking, tests, and build all pass.
- [ ] The README explains setup, use, limitations, and troubleshooting.

## New-session checklist

At the start of a future session:

1. Read `README.md` and this file.
2. Run `git status --short` and preserve existing user changes.
3. Confirm the current milestone against the live files.
4. Work only on the first incomplete task unless the user changes priorities.
5. Remember that the user writes implementation code unless they explicitly
   authorize Codex to implement it.

At the end of a milestone:

1. Run its acceptance checks.
2. Mark only verified tasks complete.
3. Update **Current handoff** with the next task and any blocker.
4. Record important design changes in the decision log below.

## Decision log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-08-01 | Treat the target as bee-inspired art, not exact bee vision. | The supplied reference is a dotted human silhouette rather than a validated biological simulation. |
| 2026-08-01 | Build one local frame-processing pipeline. | It is the smallest architecture that satisfies the current goal. |
| 2026-08-01 | Prove camera capture before segmentation or rendering. | It isolates hardware and permission problems from image-processing problems. |
| 2026-08-01 | Start segmentation with a stationary-camera foreground mask. | It avoids a model dependency until real results justify one. |
| 2026-08-08 | Replace MOG2 in the product pipeline with pretrained person segmentation after the replacement is verified. | Live testing showed that MOG2 detects motion but gradually loses a person who stands still. |
| 2026-08-01 | Use stable dot sampling. | Independent random points each frame would create distracting flicker. |
| 2026-08-01 | Use NumPy in segmentation and dot rendering. | OpenCV frames are already arrays, so NumPy directly supports required image operations. |
| 2026-08-01 | Gate pandas and Matplotlib behind offline metrics. | They provide useful tabular analysis and diagnostics without adding work to the real-time frame loop. |
