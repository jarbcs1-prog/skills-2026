# Improvement Plan: rap-writer

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 49 | **Version:** 1.0 (implied)

### Strengths
- Clear role definition (Adaptation Lyrics Master)
- 4 specific goals (word count, rhythm, rhyme, thematic relevance)
- 4 constraints with clear boundaries
- 4 skill areas defined
- 5-step workflow
- Distinctive initialization phrase

### Gaps Identified
1. **No analysis tools** - Manual analysis only, no rhythm/rhyme detection
2. **No reference library** - No rhyme dictionaries, rhythm patterns, song structures
3. **No genre support** - Only "rap" mentioned, no sub-genres (trap, boom-bap, conscious, etc.)
4. **No CLI tooling** - Manual skill only
5. **No validation** - No way to verify word count/rhythm/rhyme match
6. **No batch processing** - Single song only
7. **No style profiles** - One "master" style only
8. **No collaboration features** - No verse/hook/bridge structure
9. **No export formats** - Text only
10. **No examples** - No before/after demonstrations

---

## Improvement Roadmap

### Phase 1: Analysis Engine (Week 1)
- [ ] Build rhythm analyzer (syllable counting, stress patterns, meter detection)
- [ ] Build rhyme analyzer (end rhymes, internal rhymes, slant rhymes, multisyllabic)
- [ ] Add song structure detection (verse, chorus, bridge, intro, outro)
- [ ] Create reference library (rhyme dictionaries, rhythm patterns by genre)

### Phase 2: Generation Engine (Week 2)
- [ ] Implement constrained generation (word count, rhythm, rhyme preservation)
- [ ] Add genre-specific style profiles (trap, boom-bap, conscious, drill, UK grime, etc.)
- [ ] Support multi-part structure (verse/chorus/bridge with different patterns)
- [ ] Add collaboration mode (multiple voices, call-and-response)

### Phase 3: Tooling & Validation (Week 3)
- [ ] Create CLI: analyze, write, validate, batch
- [ ] Add validation metrics (word count accuracy, rhythm similarity, rhyme density)
- [ ] Implement batch processing for albums/playlists
- [ ] Export formats: text, LRC (lyrics with timestamps), JSON

### Phase 4: Advanced Features (Week 4)
- [ ] Add beat synchronization (BPM, time signature awareness)
- [ ] Implement flow variation (triplets, syncopation, double-time)
- [ ] Add ad-lib generation
- [ ] Create remix/adaptation mode (change genre, tempo, theme)

---

## Specific Technical Tasks

### Rhythm Analyzer
```python
# rhythm.py
class RhythmAnalyzer:
    def analyze(self, lyrics: str) -> RhythmAnalysis:
        lines = lyrics.split('\n')
        return RhythmAnalysis(
            lines=[self.analyze_line(line) for line in lines],
            overall_meter=self.detect_meter(lines),
            tempo_hint=self.estimate_tempo(lines)
        )
    
    def analyze_line(self, line: str) -> LineRhythm:
        # Syllable count (CMUdict + fallback)
        # Stress pattern (primary/secondary/unstressed)
        # Meter classification (iambic, trochaic, anapestic, etc.)
        # Pause/caesura detection
        pass
    
    def detect_meter(self, lines: List[str]) -> Meter:
        # Statistical analysis of stress patterns
        pass
```

### Rhyme Analyzer
```python
# rhyme.py
class RhymeAnalyzer:
    def __init__(self):
        self.cmu_dict = cmudict.dict()
        self.rhyme_index = self.build_rhyme_index()
    
    def analyze(self, lyrics: str) -> RhymeAnalysis:
        lines = lyrics.split('\n')
        return RhymeAnalysis(
            end_rhymes=self.find_end_rhymes(lines),
            internal_rhymes=self.find_internal_rhymes(lines),
            rhyme_scheme=self.detect_scheme(lines),
            multisyllabic=self.find_multisyllabic(lines),
            density=self.calculate_density(lines)
        )
    
    def find_end_rhymes(self, lines: List[str]) -> List[RhymePair]:
        # Group by last word phonemes
        # Detect perfect, slant, assonance, consonance
        pass
```

### Constrained Generator
```python
# generator.py
class RapGenerator:
    def __init__(self, style: StyleProfile = None):
        self.style = style or STYLE_PROFILES["boom-bap"]
    
    def adapt(self, original: str, theme: str, 
              constraints: AdaptationConstraints) -> AdaptedLyrics:
        # 1. Analyze original (rhythm, rhyme, structure)
        # 2. Generate candidate lines matching constraints
        # 3. Score candidates (thematic relevance, flow, creativity)
        # 4. Select best matching all constraints
        # 5. Validate output
        pass
    
    def generate_original(self, theme: str, structure: SongStructure,
                          style: StyleProfile) -> Lyrics:
        # Full generation from scratch
        pass
```

### Style Profiles
```python
# styles.py
STYLE_PROFILES = {
    "boom-bap": StyleProfile(
        name="boom-bap",
        bpm_range=(85, 95),
        time_signature="4/4",
        rhyme_density=0.7,
        multisyllabic_freq=0.6,
        internal_rhyme_freq=0.4,
        vocabulary_level="street_poetic",
        flow_patterns=["straight", "syncopated"],
        typical_structure=["verse", "chorus", "verse", "chorus", "bridge", "chorus"]
    ),
    "trap": StyleProfile(
        name="trap",
        bpm_range=(130, 160),
        time_signature="4/4",
        rhyme_density=0.5,
        multisyllabic_freq=0.3,
        internal_rhyme_freq=0.2,
        vocabulary_level="street_modern",
        flow_patterns=["triplet", "double_time", "straight"],
        typical_structure=["verse", "chorus", "verse", "chorus", "verse", "chorus"]
    ),
    "conscious": StyleProfile(
        name="conscious",
        bpm_range=(80, 95),
        time_signature="4/4",
        rhyme_density=0.8,
        multisyllabic_freq=0.7,
        internal_rhyme_freq=0.5,
        vocabulary_level="literary_philosophical",
        flow_patterns=["straight", "syncopated", "rubato"],
        typical_structure=["verse", "verse", "chorus", "verse", "chorus", "outro"]
    ),
    # ... more styles
}
```

### CLI Design
```bash
# rap-writer analyze --lyrics "original.txt" --output analysis.json
# rap-writer adapt --original "song.txt" --theme "climate change" --style boom-bap
# rap-writer write --theme "startup life" --structure verse-chorus --style trap --bars 16
# rap-writer validate --original "orig.txt" --adapted "adapted.txt" --strict
# rap-writer batch --theme "daily struggles" --styles boom-bap,trap,conscious --count 3
# rap-writer export --lyrics adapted.txt --format lrc --bpm 90
```

---

## Acceptance Criteria
- [ ] Rhythm analysis accuracy >90% vs manual annotation
- [ ] Rhyme detection finds >95% of end rhymes
- [ ] Adaptation preserves word count 100%, rhythm >90%, rhyme >85%
- [ ] Generation produces coherent lyrics >80% human-rated quality
- [ ] CLI completes adaptation in <10s for 16-bar verse
- [ ] Style profiles produce distinguishable outputs
- [ ] Batch processes 10 songs in <60s

---

## Dependencies
- `code-quality` (CLI code)
- `verification-before-completion` (quality claims)
- `human-writer-simulator` (creative writing enhancement)
- `ghostwriter-pro-ai` (professional writing)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Constraint satisfaction | High | High | Constraint solver, validation loop |
| Creative quality | Medium | High | Human evaluation, style profiles |
| Cultural sensitivity | Low | Critical | Content filters, style guidelines |
| Copyright issues | Low | High | Original generation only, no sampling |

---

## Success Metrics
- Word count preservation: 100%
- Rhythm similarity: >0.85 correlation
- Rhyme preservation: >85% scheme match
- Human quality rating: >4/5
- Genre classification accuracy: >90%