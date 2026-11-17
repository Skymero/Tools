### Video Editing Timeline

| Video order | Generated order | Filename            | Time        | Image                         | Narrative purpose                                                                       |
| ----------: | --------------: | ------------------- | ----------- | ----------------------------- | --------------------------------------------------------------------------------------- |
|           1 |               9 | `BD-CH1-img-9.png`  | 0:00–0:35   | Conservatory exterior         | Hook + establish the scale of the scientific city                                       |
|           2 |               1 | `BD-CH1-img-1.png`  | 0:35–1:25   | Kellie working late           | Introduce Kellie, her exhaustion, and the nursery                                       |
|           3 |              10 | `BD-CH1-img-10.png` | 1:25–1:55   | Empty late-night transit      | Show indirectly that most of the city has already stopped working                       |
|           4 |               2 | `BD-CH1-img-2.png`  | 1:55–3:15   | Bram and Kellie at bench      | Establish their workplace dynamic and Bram's new assignment                             |
|           5 |              11 | `BD-CH1-img-11.png` | 3:15–3:50   | Bram investor tour            | Explain Bram's status, competence, and why Kellie's feelings toward him are complicated |
|           6 |               3 | `BD-CH1-img-3.png`  | 3:50–4:35   | Notebook plant-shop plans     | Introduce Kellie's goal of opening her own plant shop                                   |
|           7 |              12 | `BD-CH1-img-12.png` | 4:35–5:10   | Imagined finished plant shop  | Show the quiet, achievable future Kellie actually wants                                 |
|           8 |               4 | `BD-CH1-img-4.png`  | 5:10–6:10   | Entrance to Room Three        | Transition from workplace comedy into mystery                                           |
|           9 |              13 | `BD-CH1-img-13.png` | 6:10–6:50   | Environmental-system cutaway  | Foreshadow how an airborne contaminant could escape unnoticed                           |
|          10 |               5 | `BD-CH1-img-5.png`  | 6:50–8:15   | Specimen 17 investigation     | Let Kellie investigate the mystery through botanical science                            |
|          11 |               6 | `BD-CH1-img-6.png`  | 8:15–9:35   | Aerosol close-up              | Reveal that specimen seventeen is releasing something abnormal                          |
|          12 |              14 | `BD-CH1-img-14.png` | 9:35–10:35  | Kellie's POV slipping         | Begin destabilizing Kellie's perception before the explicit hallucination               |
|          13 |               7 | `BD-CH1-img-7.png`  | 10:35–12:40 | Bram face in specimen 17      | First unmistakable psychological break                                                  |
|          14 |               8 | `BD-CH1-img-8.png`  | 12:40–15:00 | Wide Room Three / specimen 19 | Escalate from one hallucination to an entire room she can no longer trust               |

### FFmpeg Scene Structure

```python
scenes = [
    {
        "name": "conservatory_exterior",
        "image": "BD-CH1-img-9.png",
        "start": 0,
        "end": 35,
        "motion": "push_in",
        "intensity": 0.06,
    },

    {
        "name": "kellie_working_late",
        "image": "BD-CH1-img-1.png",
        "start": 35,
        "end": 85,
        "motion": "push_in",
        "intensity": 0.05,
    },

    {
        "name": "late_night_transit",
        "image": "BD-CH1-img-10.png",
        "start": 85,
        "end": 115,
        "motion": "pan_right",
        "intensity": 0.05,
    },

    {
        "name": "bram_assignment",
        "image": "BD-CH1-img-2.png",
        "start": 115,
        "end": 195,
        "motion": "push_in",
        "intensity": 0.05,
    },

    {
        "name": "investor_tour",
        "image": "BD-CH1-img-11.png",
        "start": 195,
        "end": 230,
        "motion": "pan_left",
        "intensity": 0.06,
    },

    {
        "name": "shop_notebook",
        "image": "BD-CH1-img-3.png",
        "start": 230,
        "end": 275,
        "motion": "push_in",
        "intensity": 0.08,
    },

    {
        "name": "imagined_shop",
        "image": "BD-CH1-img-12.png",
        "start": 275,
        "end": 310,
        "motion": "pull_out",
        "intensity": 0.05,
    },

    {
        "name": "room_three_entrance",
        "image": "BD-CH1-img-4.png",
        "start": 310,
        "end": 370,
        "motion": "push_in",
        "intensity": 0.08,
    },

    {
        "name": "environment_cutaway",
        "image": "BD-CH1-img-13.png",
        "start": 370,
        "end": 410,
        "motion": "pan_right",
        "intensity": 0.04,
    },

    {
        "name": "specimen_17",
        "image": "BD-CH1-img-5.png",
        "start": 410,
        "end": 495,
        "motion": "push_in",
        "intensity": 0.07,
    },

    {
        "name": "aerosol",
        "image": "BD-CH1-img-6.png",
        "start": 495,
        "end": 575,
        "motion": "push_in",
        "intensity": 0.10,
    },

    {
        "name": "pov_slipping",
        "image": "BD-CH1-img-14.png",
        "start": 575,
        "end": 635,
        "motion": "static",
        "intensity": 0.01,
    },

    {
        "name": "first_bram_face",
        "image": "BD-CH1-img-7.png",
        "start": 635,
        "end": 760,
        "motion": "push_in",
        "intensity": 0.08,
    },

    {
        "name": "plants_laughing",
        "image": "BD-CH1-img-8.png",
        "start": 760,
        "end": 900,
        "motion": "pull_out",
        "intensity": 0.08,
    },
]
```
