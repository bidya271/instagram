# Standard Operating Procedure: Short-Form Video Production
**Channel**: `@unwrittenrules.b3` (TikTok, Instagram) / `Unwrittenrules.B3` (YouTube)  
**Core IP Library**: [**`books/`**](file:///Users/bidya/Documents/book/)
1. *The Ideology of Hypocrisy* (`books/1. hypocrisy`) — Virtue signaling, double standards, self-preservation
2. *The Architecture of Greed* (`books/2.greed`) — Scarcity mindset, wealth as a scoreboard, incentive design
3. *The Gravity of Power* (`books/3. power`) — Obedience, institutional shields, corporate thrones, asymmetric leverage
4. *Status: The Currency of Envy* (`books/4. status`) — Social comparison, peer competition, corporate posturing
5. *The Morality Machine* (`books/5. morality_machine`) — Ethical illusions, institutional compliance theater
6. *AI Production Handbook* (`books/ai-handbook`) — Systems architecture, agent orchestration, systemic disruption

**Objective**: Build a loyal audience around dark psychology, human nature, stoicism, and unwritten power dynamics, converting viewers indirectly into readers across the entire book catalog.

---

## 1. Visual Aesthetics Standard
- **Resolution & Aspect Ratio**: 1080×1920 (9:16 vertical), 30–60 fps.
- **Footage Sourcing & Zero-Reuse Rule**:
  - Each reel MUST feature a fresh, unique optical background clip (twilight mountain ridges, mist over coastlines, brooding cityscapes, rain on asphalt, ocean waves, quiet forests).
  - **Never repeat a footage clip across reels.**
  - Active clips reside in `assets/footage/`. As soon as a reel is published, the source clip is moved into `assets/footage/used/` so the system never re-uses it.
  - Never use low-res horizontal crops or synthetic AI plastic renders.
- **UI & Layout Rule**: **Strictly ZERO artificial UI cards, borders, progress bars, or plastic graphics.**
- **Typography**:
  - Font: `Playfair Display`, italic serif, 56–60px.
  - Text Shadow: `0 4px 35px rgba(0, 0, 0, 0.95), 0 2px 10px rgba(0, 0, 0, 0.9)`.
  - Viewport Placement: Centered in the upper negative space (25%–42% from top) so text never collides with horizon lines or bright light sources.
- **Attribution Signature**:
  - Text: `@unwrittenrules.b3 • The Ideology of Hypocrisy`
  - Font: Clean sans-serif (`Inter` / system sans), uppercase, letter spacing `0.14em`, opacity `0.72`.
  - Position: `bottom: 220px` (guarantees zero overlap with platform caption/UI banners).

---

## 2. Voiceover & Narration Standard
- **Voice Actor**: `en-US-ChristopherNeural` (Calm, heavy, punchy, authoritative, masculine).
- **Studio Mastering Chain (FFmpeg)**:
  ```bash
  ffmpeg -i raw_voice.mp3 -af "equalizer=f=130:t=q:w=1:g=3.5,equalizer=f=400:t=q:w=1.5:g=-2.5,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=50" -b:a 192k mastered_voice.mp3
  ```
- **Pacing**: Deliberate, 150–165 words per minute. Punctuate hooks and takeaways with 0.8–1.2s silence pauses to let truths register.

---

## 3. Approved Audio Presets (The "Standard Trio")
*Synthetic ambient drones, cheerful lo-fi beats, and sweet vlog melodies are strictly banned.*

1. **Preset 2A ("Solitude Intro")**:
   - Track: *M83 — Solitude (Felsmann + Tiley Reinterpretation)* [0:00 – 0:12]
   - Tone: Deep, brooding, mysterious, quiet power.
2. **Preset 2B ("Solitude Build")**:
   - Track: *M83 — Solitude (Felsmann + Tiley Reinterpretation)* [0:44 – 0:56]
   - Tone: Emotional crescendo, synth swell on the final punchline.
3. **Preset 3 ("Interstellar Grand Piano")**:
   - Track: *Cornfield Chase (Dorian Marko Piano Cover)* [0:00 – 0:12]
   - Tone: Cosmic, breathtaking, intricate neoclassical piano.

**Audio Engineering**:
- Vocal volume: `1.15` to `1.20`.
- Music volume: ducked to `0.20` – `0.24` (`-18 dB` to `-20 dB`).
- Outro: 1.2-second smooth fade (`afade=t=out:st=10.3:d=1.2`).

---

## 4. Multi-Platform Distribution Pipeline (Buffer)
- **YouTube Shorts Channel**: `Unwrittenrules.B3` (`6ad106eb778b240e2f1b44d4`)
  - Category: `22` (People & Blogs)
  - Format: `#shorts` in title and description.
- **Instagram Reels**: `unwrittenrules.b3` (`6ad106c2778b240e2f1b3b33`)
  - Type: `reel`, `shouldShareToFeed: true`
- **TikTok**: `unwrittenrules.b3` (`6ad106fe778b240e2f1b46ee`)
  - Direct short video posting with hashtag cluster (`#unwrittenrules`, `#protectyourpeace`, `#stoicism`, `#psychology`).
