# IPL Cricket Analytics — Analysis Report

## 1. H2 — Chase Success by Target Band

### Question
How does chase success vary across first-innings target bands?

### Number
The analysis compares chase win rate across different first-innings target bands.

### Population
Completed IPL matches with a valid first-innings score and a recorded match result.

### Decision
The target-band comparison can help identify whether chase success changes as the required target increases.

### Doubt
The number of matches in each target band is not equal, and other factors such as team strength, venue, and match conditions may also affect the result.

**Chart:** `reports/figures/chase_win_rate_target_band.png`

---

## 2. C1 — Run Scoring and Wicket Risk by Innings Phase

### Question
How do scoring rate and wicket-taking rate change across the innings?

### Number
The analysis compares runs per over and wickets per 100 legal balls across the Powerplay, Middle Overs, and Death phases.

### Population
Legal deliveries from the analyzed IPL matches grouped into the three innings phases.

### Decision
The phase comparison can help describe how scoring and wicket-taking patterns change during an innings.

### Doubt
The relationship between scoring and wickets does not establish that one directly causes the other. Team quality and match situation may also influence the results.

**Chart:** `reports/figures/runs_wickets_by_phase.png`

---

## 3. G3 — Toss Decision and Match Win Rate

### Question
How often does the team making each toss decision go on to win the match?

### Number
The chart compares match win rate between the available toss decisions.

### Population
Completed matches with a recorded toss decision and match winner.

### Decision
The comparison provides a descriptive view of the relationship between toss decision and match outcome.

### Doubt
A difference in win rate does not prove that the toss decision itself caused the difference. Venue, teams, conditions, and match strategy may also contribute.

**Chart:** `reports/figures/toss_split.png`

---

## 4. I1 — Venue Cleaning

### Question
How does venue-name cleaning affect the venue match-count leaderboard?

### Number
The analysis compares the number of matches associated with venue names before and after the cleaning process.

### Population
Matches with recorded venue information in the raw and cleaned match datasets.

### Decision
Venue cleaning helps provide a more consistent basis for venue-level analysis and comparison.

### Doubt
The result depends on the cleaning and deduplication rules used. Different legitimate venue naming conventions may require different mappings.

**Chart:** `reports/figures/venue_before_after.png`

---

## 5. Specialism — Data Analytics: Seasonal Scoring Pattern

### Question
How does the average first-innings score change across IPL seasons?

### Number
The analysis compares the average first-innings score for each season and displays the number of matches used for each season.

### Population
Completed matches with a valid first-innings score and recorded season information.

### Decision
The seasonal comparison provides a descriptive view of how first-innings scoring has varied across the dataset.

### Doubt
Changes between seasons may reflect differences in teams, venues, playing conditions, competition format, or other factors. The chart describes the pattern but does not establish a single cause.

**Chart:** `reports/figures/specialism_season_scoring.png`

---

## Least-Confident Findings

1. **Toss decision and match win rate** — The comparison does not establish causation.
2. **Seasonal scoring pattern** — Differences between seasons may have multiple contributing factors.
3. **Venue cleaning comparison** — Results depend on the cleaning and deduplication rules.

---

## Conclusion

The analysis uses five decision-focused findings covering chase success, innings phases, toss decisions, venue cleaning, and seasonal scoring patterns. Each finding includes its population, key measurement, decision relevance, and an important limitation or doubt.