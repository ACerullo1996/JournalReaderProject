import os


def load_env_file(env_path: str = ".env") -> None:
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()


KEYWORDS = [
    "rhyth", "rhythm", "entrain", "oscill", "beta", "mu", "alpha", "sensorimotor", "motor cortex",
    "action observation", "motor imagery", "audiovisual", "eeg", "vr",
    "coherence", "itpc", "ssvep", "pac", "ssmvep",
    "ASSR", "Auditory", "steady state response", "click train", "white noise"
]

SYSTEM_PROMPT = """
You are a scientific research assistant specialized in neural engineering, EEG, fNIRS, and multimodal neuroimaging.

Your role is to extract, summarize, and contextualize information from peer-reviewed research papers in a structured, concise, and technically precise manner.

General Rules:
- Assume the paper may be dense, highly technical, or incomplete in reporting.
- Do NOT infer, guess, or hallucinate information.
- If any requested detail is not explicitly stated, write: "Not reported".
- Preserve the authors' terminology, uncertainty, and level of evidence.
- Maintain a strict separation between results, interpretation, limitations, and relevance, as defined by each section prompt.

Audience:
- Write for a PhD-level researcher in neural engineering and systems neuroscience.

Project Context (for relevance and alignment only):
The researcher's project investigates how rhythmic auditory-visual stimulation presented in a controlled virtual reality environment modulates sensorimotor brain activity during action observation and motor imagery. The study uses EEG/fNIRS-based measures of neural oscillations and cortical entrainment to compare rhythmic and nonrhythmic multimodal stimuli, with the goal of improving understanding of multisensory sensorimotor integration and informing neural decoding strategies for brain-computer interface and neurorehabilitation applications. This is specifically NOT an fMRI Study.

Hypothesis (contextual reference only):
Temporally rhythmic, synchronized audiovisual stimulation in VR is hypothesized to produce stronger cortical entrainment and sensorimotor mu/beta modulation than nonrhythmic or mismatched stimulation, with additional enhancement during action observation and motor imagery.

Scope and Alignment Rules:
- Use the project context to assess relevance (Section 7) and to emphasize pertinent aspects of studies when appropriate (Section 8).
- Do NOT force alignment with the project if a paper is not clearly relevant.
- Do NOT reinterpret results to fit the project hypothesis.
- Field-facing summaries (e.g., results, interpretation, introduction-ready summaries) must remain neutral and grounded in the authors' reported findings.
- Papers using fMRI are not useful
""".strip()

SECTION_PROMPTS = {
    1: """SECTION 1: METADATA

Task:
Extract ONLY bibliographic and publication metadata from the paper.
Do NOT summarize study content, methods, or results.

General Rules:
- Use information explicitly stated in the paper whenever possible.
- If any item is missing, unclear, or not explicitly stated, write: "Not reported".
- Do NOT infer bibliographic details such as journal name, year, or authorship.

Return the following fields exactly as listed:

Paper Title
- Full title as it appears in the paper

Authors
- List all authors in the order presented
- If affiliations are provided, do NOT include them

Year of Publication
- Year only (YYYY)
- If multiple years appear (e.g., online vs. print), use the year explicitly associated with publication

Journal or Conference
- Full journal or conference name
- Do NOT abbreviate unless the abbreviation is used by the authors

Impact Factor
- Report ONLY if explicitly stated in the paper
- Otherwise, write: "Not reported"
- Do NOT look up or estimate impact factors

Keywords
- If author-provided keywords are listed, reproduce them verbatim
- If no keywords are listed, infer a short set (3-6 items) from the abstract and clearly label them as: "Inferred keywords"

Constraints:
- Do NOT introduce external knowledge
- Do NOT infer missing bibliographic fields
- Do NOT include DOI, PMID, or citation formatting
- Preserve original capitalization and spelling where possible

""",
    2: """SECTION 2: EXPERIMENTAL DESIGN

Task:
Summarize ONLY the experimental design and methods of the paper.
Focus strictly on what was done.
Do NOT report results, outcomes, or interpretations.

General Rules:
- Describe procedures, stimuli, and analyses exactly as reported by the authors.
- If any required detail is missing or unclear, write: "Not reported".
- Do NOT infer design choices or analytical intent.

Organize your response under the following headings:

Experimental Tasks and Conditions
- Description of tasks performed by participants
- Experimental conditions or manipulations
- Task instructions relevant to neural measurement
- Within-subject vs between-subject design (if specified)

Stimulus Properties
- Sensory modality: auditory, visual, audiovisual, or multimodal
- Rhythmic vs non-rhythmic structure (including frequencies or tempos, if reported)
- Stimulus duration, intensity, and presentation format
- Synchronization or phase relationships between modalities (if applicable)

Recording Modalities
- Neuroimaging or physiological modalities used (EEG, fNIRS, EMG, MEG, etc.)
- Hardware, sampling rate, and electrode/optode configuration (if reported)
- Any simultaneous or multimodal recordings

Brain Regions of Interest
- Cortical or subcortical regions explicitly targeted or analyzed
- ROI definitions or electrode groupings, if described
- Hemispheric specificity, if reported

Participants
- Sample size
- Population characteristics (age, handedness, clinical status, etc.)
- Inclusion/exclusion criteria, if reported

Trial Structure and Timing
- Trial sequence and phases
- Duration of stimuli, tasks, and rest periods
- Number of trials, blocks, and repetitions
- Total session duration, if reported

Control Conditions
- Control or comparison conditions included in the design
- Baseline or rest conditions
- Counterbalancing or randomization procedures, if reported

Statistical Models and Comparisons
- Statistical models used (e.g., ANOVA, linear mixed-effects models, regression)
- Factors, contrasts, or comparisons specified by the authors
- Correction methods for multiple comparisons, if reported

Constraints:
- Do NOT restate results or effect directions
- Do NOT introduce interpretations or motivations
- Do NOT speculate about design rationale beyond what is stated
- Preserve the authors' terminology and level of detail

""",
    3: """SECTION 3: RESULTS

Task:
Summarize ONLY the empirical results explicitly reported in the paper.
This section must be strictly descriptive.
Do NOT interpret, explain, or speculate about mechanisms or implications.

General Rules:
- Report only findings directly stated in the Results (or equivalent) section.
- Use the authors' terminology and level of certainty.
- If a category is not reported, write: "Not reported".
- Do NOT restate methods or task descriptions (those belong in Section 2).

Organize your response under the following headings:

Spatial Regions of Interest
- Brain regions explicitly analyzed or reported (e.g., M1, SMA, PMC, sensorimotor cortex, visual cortex)
- Report hemispheric specificity if stated
- If regions are averaged into ROIs, state how (if reported)

Spectral Features
- Frequency bands explicitly reported (e.g., delta, theta, alpha/mu, low beta, high beta, gamma)
- Measures used (e.g., power, ERD/ERS, coherence, ITPC, PAC, SSVEP)
- Direction of effects (increase/decrease) ONLY if explicitly stated

Temporal Dynamics
- Timing of effects relative to stimulus or task events
- Transient vs sustained responses
- Latency, duration, or time-resolved patterns, if reported

Group or Condition Differences
- Differences between experimental conditions, groups, or task phases
- Within-subject vs between-group effects, if specified
- If no comparisons are reported, write: "Not reported"

Effect Sizes and Statistical Significance
- Statistical tests used (e.g., ANOVA, LMM, t-tests, cluster tests), if reported
- Effect sizes, confidence intervals, or p-values, if explicitly stated
- If statistics are mentioned qualitatively only, reflect that exactly

Constraints:
- Do NOT use interpretive language (e.g., "suggests", "supports", "indicates")
- Do NOT attribute meaning to observed effects
- Do NOT infer neural mechanisms
- Preserve uncertainty and qualifiers used by the authors

""",
    4: """SECTION 4: INTERPRETATION

Task:
Summarize how the authors interpret and contextualize their results.
This section should reflect the authors' reasoning and conclusions only.
Do NOT introduce new interpretations or reanalyze the data.

Organize your response under the following headings:

Primary Conclusions
- The main conclusions explicitly drawn by the authors
- Statements about what the results demonstrate, suggest, or support
- If conclusions are tentative or qualified, preserve the authors' level of certainty

Proposed Neural Mechanisms
- Neural or cognitive mechanisms proposed by the authors (e.g., neural entrainment, sensorimotor integration, predictive timing, motor preparation, multisensory coupling)
- Clearly distinguish between mechanisms the authors *support* versus those they merely *speculate about*
- If no mechanisms are discussed, write: "Not explicitly discussed."

Relation to Prior Literature
- How the authors position their findings relative to existing work
- Explicit statements of agreement, extension, refinement, or disagreement with prior studies
- References to established frameworks or models used to interpret results

Constraints:
- Do NOT restate detailed results (those belong in Section 3)
- Do NOT introduce new hypotheses, mechanisms, or critiques
- Do NOT elevate speculative language beyond what the authors use
- Use neutral, attribution-focused phrasing (e.g., "the authors suggest...", "the authors interpret this as...")

""",
    5: """SECTION 5: LIMITATIONS & FUTURE WORK

Task:
Identify and summarize the limitations, open questions, and future research directions discussed by the authors, based only on information explicitly present in the paper.

Organize your response under the following headings:

Author-Acknowledged Limitations
- Limitations explicitly stated by the authors
- Sample size, population, task design, stimulus control, modality constraints, analytical limitations, or statistical considerations
- If none are stated, write: "Not explicitly discussed by the authors."

Methodological Constraints
- Practical or technical constraints inherent to the study design (e.g., EEG spatial resolution, limited frequency range, lack of control conditions), but only if explicitly mentioned or clearly acknowledged by the authors
- If not discussed, write: "Not reported."

Open Questions / Knowledge Gaps
- Unresolved questions or gaps identified by the authors
- Ambiguities in mechanisms, generalizability, or interpretation
- Do NOT introduce new gaps not mentioned or implied by the authors

Proposed Future Directions
- Future experiments, analyses, or extensions explicitly suggested by the authors
- Broader implications or next steps mentioned in the discussion or conclusion

Project Awareness:
- When applicable, briefly note whether any limitation, gap, or future direction is directly relevant to my project.
- Do NOT force relevance; if no clear connection exists, omit this note.

Constraints:
- Do NOT speculate beyond the authors' statements
- Do NOT reframe limitations as strengths
- Do NOT introduce new hypotheses or experimental ideas
- Use precise, neutral academic language
""",
    6: """SECTION 6: KEY REFERENCES

Task:
Identify the most influential, foundational, or frequently referenced works that the authors rely on in this paper, based only on information explicitly present in the text.

In addition to general importance, prioritize references that are most relevant to my research project.

Selection Criteria (one or more must apply):
- Repeatedly cited or emphasized by the authors
- Used to motivate the study's hypothesis or experimental design
- Central to the theoretical framework or analytical approach
- Serves as a benchmark, comparison, or methodological reference
- Directly informs paradigms, analyses, or interpretations relevant to my project

Return:
- A short list (typically 3-6 items) of key references
- Proper MLA citations WHEN sufficient bibliographic information is available
- If any citation field is missing, write "Not reported" for that field
- A single concise sentence per reference explaining:
  (a) why it is important to this paper, and
  (b) how it connects to my project (if applicable)

Constraints:
- Do NOT invent or infer bibliographic details that are not explicitly stated
- Do NOT list every reference; prioritize only those central to the paper's contribution
- Do NOT force relevance-if a reference is important to the paper but not clearly related to my project, state that explicitly
""",
    7: """SECTION 7: RELEVANCE TO MY PROJECT
Task:
Assess how relevant this paper is to my research project and briefly justify that assessment.

First, assign ONE of the following relevance levels:
- Highly Relevant
- Relevant
- Loosely Relevant
- Not Relevant

Then, write a concise 1-2 sentence explanation supporting the assigned level.

Relevance Definitions:
- Highly Relevant:
  The paper directly investigates multiple core components of the project described in the system prompt.

- Relevant:
  The paper directly investigates at least one core component of the project described in the system prompt.

- Loosely Relevant:
  The paper is methodologically, conceptually, or theoretically related to the project described in the system prompt, but does not directly examine its key paradigms or mechanisms.

- Not Relevant:
  The paper does not meaningfully relate to the project described in the system prompt.

Writing Constraints:
- Be specific about *what* aspect of the study determines its relevance (paradigm, modality, brain region, frequency band, or analytical approach).
- Use neutral, reviewer-safe language (e.g., "informs", "motivates", "is relevant to").
- Do NOT restate the paper's full findings.
- Do NOT speculate beyond what is explicitly reported.
- Do NOT force relevance; if the connection is weak or absent, state that clearly.

Output Format:
Relevance Level: <Highly Relevant | Relevant | Loosely Relevant | Not Relevant>
Explanation: <1-2 sentences>
""",
    8: """SECTION 8: INTRODUCTION-READY SUMMARY

Task:
Write a polished 1-2 sentence summary of the results of the study that is suitable for direct inclusion in the introduction of a journal manuscript focusing on my project.
When appropriate, emphasize aspects of the study (e.g., paradigm, modality, brain region, or analytical approach) that are relevant to my project, without explicitly referring to "my project" or forcing relevance.

Phrase Control:
- Prefer SAFE phrasing for descriptive statements (e.g., "Previous work has shown that...", "A study by {Author et al.} ({Year}) reported...").
- Use BOLD phrasing only if the results are strong and explicitly supported (e.g., "These findings support the role of...").
- Use SPECULATIVE phrasing only when transitioning toward interpretation, future work, or hypothesis framing (e.g., "These results may reflect...").

Structure Guidance:
- Sentence 1: Situate the study within prior literature or methodological context.
- Sentence 2 (optional): State the key contribution or implication of the study, using conservative, reviewer-safe language.

Writing Constraints:
- Use formal academic language appropriate for neuroscience, neural engineering, and EEG-based research.
- Maintain stylistic consistency with high-impact journals (e.g., NeuroImage, IEEE TBME, Journal of Neural Engineering).
- Rotate phrasing to avoid repetitive sentence openings across papers.
- Do NOT reference figures, tables, section numbers, or supplemental materials.
- Do NOT restate detailed numerical results, statistics, or methodological details.
- Preserve the authors' level of certainty and any explicit qualifications.
- Do not overgeneralize findings.
- Do not introduce interpretations not explicitly stated by the authors.
- Output plain text only.
- Do NOT use Markdown, boldface, italics, bullet points, or special formatting.
""",
}

MODEL_PAPER = "gpt-4o"

RELEVANCE_LABELS = (
    "Highly Relevant",
    "Relevant",
    "Loosely Relevant",
    "Not Relevant",
)

KEYWORDS = [
    "rhyth", "rhythm", "entrain", "oscill", "beta", "mu", "alpha", "sensorimotor", "motor cortex",
    "action observation", "motor imagery", "audiovisual", "eeg", "vr",
    "coherence", "itpc", "ssvep", "pac", "ssmvep",
    "ASSR", "Auditory", "steady state response", "click train", "white noise"
]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
