# ✨ Unit 6 — Generative AI Fundamentals

> **Module**: Module 4 — Generative AI  
> **Duration**: Day 12–13 (16 hours)  
> **Dates**: 14-Jul-2026, 15-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — What is Generative AI?

### Q1. What is Generative AI? How is it different from traditional AI/ML?

**A:** **Generative AI** is a category of AI that **creates new content** — text, images, code, audio, video — rather than just analyzing or classifying existing data.

| Aspect | Traditional ML (Discriminative) | Generative AI |
|--------|-------------------------------|---------------|
| **Task** | Classify, predict, detect | Create, generate, synthesize |
| **Output** | Label, number, category | New text, image, code, audio |
| **Example** | "Is this email spam?" → Yes/No | "Write an email about project update" → Full email |
| **Models** | Random Forest, SVM, Logistic Regression | GPT, Gemini, DALL-E, Stable Diffusion |
| **Training** | Learn boundaries between classes | Learn the underlying distribution of data |

**Key insight:** Traditional ML answers questions about existing data. Generative AI creates data that didn't exist before.

---

### Q2. What are the main types of generative AI?

**A:**

| Type | What It Generates | Key Models | Use Case |
|------|-------------------|------------|----------|
| **Text Generation** | Natural language text | GPT-4, Gemini, Claude, LLaMA | Chatbots, writing, summarization |
| **Image Generation** | Images from text prompts | DALL-E, Midjourney, Stable Diffusion | Art, design, product mockups |
| **Code Generation** | Source code | GitHub Copilot, Codex, Gemini | Autocomplete, code writing |
| **Audio Generation** | Speech, music | Eleven Labs, MusicLM, Bark | Voice synthesis, music creation |
| **Video Generation** | Video clips | Sora (OpenAI), Runway | Film, marketing, animation |
| **3D Generation** | 3D models | Point-E, GET3D | Gaming, architecture, VR |
| **Multimodal** | Text + images + audio | GPT-4o, Gemini | Analyze images, generate from mixed inputs |

---

### Q3. What are Large Language Models (LLMs)?

**A:** **LLMs** are deep learning models trained on massive text datasets to understand and generate human language. They are the foundation of modern text-based generative AI.

**Key characteristics:**
- **Large** — Billions of parameters (GPT-4: ~1.8T, Gemini Ultra: unknown, LLaMA 3: 405B).
- **Pretrained** — Trained on vast internet text (books, websites, code, articles).
- **General purpose** — Can do many tasks: Q&A, summarization, translation, coding, reasoning.
- **Next-token prediction** — Trained to predict the next word given previous words.

**Major LLMs:**

| Model | Company | Notable Feature |
|-------|---------|----------------|
| **GPT-4 / GPT-4o** | OpenAI | Multimodal, strong reasoning |
| **Gemini** | Google DeepMind | Multimodal native, long context |
| **Claude** | Anthropic | Long context (200K tokens), safety-focused |
| **LLaMA 3** | Meta | Open-source, high performance |
| **Mistral / Mixtral** | Mistral AI | Efficient, open-source |

---

### Q4. How are LLMs trained? Explain the training pipeline.

**A:** LLM training has three main phases:

**Phase 1 — Pre-training (most expensive):**
- Train on trillions of tokens from the internet.
- Objective: **Next-token prediction** — given a sequence, predict the next word.
- Requires thousands of GPUs for weeks/months.
- Cost: millions of dollars.
- Result: A base model that can continue text but isn't conversational.

**Phase 2 — Supervised Fine-tuning (SFT):**
- Train on curated (prompt, ideal response) pairs.
- Teaches the model to follow instructions and be helpful.
- Uses human-written demonstrations.

**Phase 3 — Reinforcement Learning from Human Feedback (RLHF):**
- Humans rank model outputs from best to worst.
- Train a **reward model** on these rankings.
- Use PPO (Proximal Policy Optimization) to optimize the LLM against the reward model.
- Result: Model aligns with human preferences (helpful, harmless, honest).

```
Internet Text → Pre-training → Base Model
                                    ↓
(Prompt, Response) pairs → Fine-tuning → Instruction-following Model
                                    ↓
Human Rankings → RLHF → Aligned, Safe Model (ChatGPT, Gemini)
```

---

### Q5. What is the Transformer architecture?

**A:** The **Transformer** (from the 2017 paper "Attention Is All You Need") is the architecture behind ALL modern LLMs.

**Key innovation:** **Self-attention mechanism** — allows the model to look at ALL words in a sequence simultaneously and determine which words are most relevant to each other.

**Architecture:**
```
Input Tokens → Embedding → [Positional Encoding]
                               ↓
                    ┌──── Encoder ────┐    (used in BERT)
                    │  Self-Attention │
                    │  Feed Forward   │
                    └─────────────────┘
                               ↓
                    ┌──── Decoder ────┐    (used in GPT)
                    │  Masked Self-   │
                    │  Attention      │
                    │  Cross-Attention│
                    │  Feed Forward   │
                    └─────────────────┘
                               ↓
                    Output Tokens
```

**Types:**
- **Encoder-only** (BERT) — Understands text (classification, NER, sentiment).
- **Decoder-only** (GPT, Gemini) — Generates text (chatbots, completion).
- **Encoder-Decoder** (T5, BART) — Both understand and generate (translation, summarization).

---

### Q6. What is the attention mechanism? Why is it important?

**A:** **Attention** allows the model to focus on the most relevant parts of the input when generating each output token.

**Example:** "The cat sat on the mat because **it** was tired."
- What does "it" refer to? **The cat** (not the mat).
- Attention assigns high weight to "cat" when processing "it".

**Self-attention computation:**
1. For each token, create three vectors: **Query (Q)**, **Key (K)**, **Value (V)**.
2. Compute attention score: `Score = Q × Kᵀ / √d` (scaled dot-product).
3. Apply softmax to get attention weights (probabilities).
4. Multiply weights by Values to get output.

**Multi-head attention:** Run multiple attention computations in parallel, each focusing on different aspects (syntax, semantics, position, etc.).

**Why it matters:**
- Captures **long-range dependencies** (words far apart can relate).
- **Parallelizable** (unlike RNNs which process sequentially).
- Enables models to understand context and nuance.

---

## 🔹 Section 2 — Key GenAI Concepts

### Q7. What are tokens? Why do they matter?

**A:** **Tokens** are the basic units that LLMs process. They're not exactly words — they're subword units.

**Tokenization examples:**
```
"Hello world"     → ["Hello", " world"]         (2 tokens)
"unhappiness"     → ["un", "happiness"]          (2 tokens)
"ChatGPT is cool" → ["Chat", "G", "PT", " is", " cool"]  (5 tokens)
```

**Why tokens matter:**

| Aspect | Impact |
|--------|--------|
| **Context window** | GPT-4: 128K tokens; Gemini 1.5: 1M tokens — how much text the model can "see" at once |
| **Cost** | API pricing is per token (e.g., $0.01 per 1K input tokens) |
| **Speed** | More tokens = slower generation |
| **Limits** | Model can't process text longer than its context window |

**Rule of thumb:** 1 token ≈ 4 characters in English ≈ ¾ of a word. 1000 tokens ≈ 750 words.

---

### Q8. What is a context window?

**A:** The **context window** is the maximum number of tokens an LLM can process in a single request (input + output combined).

| Model | Context Window |
|-------|---------------|
| GPT-3.5 | 4K / 16K tokens |
| GPT-4 | 8K / 32K / 128K tokens |
| Gemini 1.5 Pro | 1M tokens |
| Claude 3 | 200K tokens |
| LLaMA 3 | 8K / 128K tokens |

**Why it matters:**
- Larger context = can process longer documents.
- RAG (Retrieval-Augmented Generation) is used when documents exceed the context window.
- Cost increases with more tokens in context.

---

### Q9. What is temperature in LLMs?

**A:** **Temperature** controls the **randomness** of the model's output.

| Temperature | Behavior | Use Case |
|-------------|---------|----------|
| **0** | Deterministic — always picks the most probable token | Factual Q&A, data extraction, code |
| **0.3-0.7** | Balanced — mostly probable but some variety | General chat, balanced creativity |
| **1.0** | More random — explores less probable tokens | Creative writing, brainstorming |
| **>1.0** | Very random — may produce incoherent output | Experimental, rarely used |

```python
# In LangChain:
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
# temperature=0 → same question always gets same answer
```

---

### Q10. What is Top-K and Top-P sampling?

**A:** These control HOW the model selects the next token from the probability distribution.

**Top-K Sampling:**
- Only consider the top K most probable tokens.
- K=1 → greedy (always pick the best) = deterministic.
- K=50 → choose from the top 50 most likely tokens.

**Top-P (Nucleus) Sampling:**
- Consider the smallest set of tokens whose cumulative probability ≥ P.
- P=0.9 → consider tokens until their probabilities sum to 90%.
- Adapts to the distribution (more or fewer tokens depending on context).

**Example:**
```
Next token probabilities:
  "the" → 0.4, "a" → 0.2, "this" → 0.15, "an" → 0.1, ...

Top-K=3:  Choose from ["the", "a", "this"]
Top-P=0.75: Choose from ["the", "a", "this"] (0.4+0.2+0.15=0.75)
```

---

### Q11. What are hallucinations in LLMs? How do you prevent them?

**A:** **Hallucination** = LLM generates information that sounds plausible but is factually incorrect or made up.

**Types:**
- **Factual hallucination:** "The Eiffel Tower is 500 meters tall" (actually 330m).
- **Source hallucination:** "According to a 2023 study by Stanford..." (study doesn't exist).
- **Logical hallucination:** Internally inconsistent reasoning.

**Prevention strategies:**

| Strategy | How It Helps |
|----------|-------------|
| **RAG** | Ground answers in retrieved documents |
| **Temperature = 0** | Deterministic; less creative, more factual |
| **Prompt engineering** | "Answer based ONLY on the provided context" |
| **Source citation** | Ask model to cite which sources it used |
| **Fallback messages** | If info not in context, say "I don't know" |
| **Fact-checking** | Verify critical outputs with external sources |
| **Fine-tuning** | Train on domain-specific, verified data |

---

### Q12. What is the difference between open-source and closed-source LLMs?

**A:**

| Aspect | Open-Source | Closed-Source |
|--------|-----------|---------------|
| **Access** | Model weights publicly available | Only accessible via API |
| **Cost** | Free to download and run | Pay per API call |
| **Customization** | Can fine-tune, modify, host yourself | Limited to API parameters |
| **Privacy** | Data stays on your infrastructure | Data sent to provider's servers |
| **Support** | Community-driven | Enterprise support |
| **Examples** | LLaMA 3, Mistral, Falcon, Phi | GPT-4, Gemini, Claude |

**When to choose open-source:**
- Data privacy is critical (healthcare, finance).
- Need full customization and fine-tuning.
- Want to avoid vendor lock-in and API costs.

**When to choose closed-source:**
- Need the best performance (GPT-4, Gemini).
- Don't want to manage infrastructure.
- Quick prototyping and development.

---

## 🔹 Section 3 — Generative AI Applications

### Q13. What are the main applications of Generative AI?

**A:**

| Domain | Application | Example |
|--------|------------|---------|
| **Customer Service** | AI chatbots, automated support | SAP Joule answering HR queries |
| **Content Creation** | Write articles, marketing copy, emails | Blog post generation, ad copy |
| **Software Development** | Code generation, debugging, testing | GitHub Copilot, code review |
| **Document Processing** | Summarization, extraction, Q&A | RAG-based document search |
| **Translation** | Language translation | Google Translate, DeepL |
| **Healthcare** | Medical report analysis, drug discovery | Analyzing patient records |
| **Education** | Tutoring, quiz generation, explanations | Khan Academy's AI tutor |
| **Finance** | Report generation, fraud analysis | Automated financial summaries |
| **Legal** | Contract review, case research | Harvey AI for legal research |
| **Creative** | Art, music, video generation | Midjourney, Sora |

---

### Q14. What are embeddings in the context of GenAI?

**A:** **Embeddings** are numerical vector representations of text (or images, audio) that capture their **semantic meaning** in a high-dimensional space.

```
"king"   → [0.2, 0.8, 0.1, ...]
"queen"  → [0.2, 0.7, 0.3, ...]    ← Close to "king" in vector space
"banana" → [0.9, 0.1, 0.4, ...]    ← Far from "king"
```

**Properties:**
- Similar texts have similar embeddings (close in vector space).
- Can capture relationships: `king - man + woman ≈ queen`.
- Dimensionality: typically 768-3072 dimensions.

**Use in GenAI:**
- **Semantic search** — Find similar documents.
- **RAG** — Retrieve relevant context for LLM prompts.
- **Clustering** — Group similar texts.
- **Classification** — Use embeddings as features for classifiers.

**Models:** `gemini-embedding-001`, `text-embedding-ada-002` (OpenAI), `all-MiniLM-L6-v2` (open source).

---

### Q15. What is fine-tuning? When should you fine-tune an LLM?

**A:** **Fine-tuning** = taking a pre-trained LLM and training it further on your specific data to specialize it for your use case.

```
Pre-trained LLM (general knowledge)
        ↓
    Fine-tune on your data
        ↓
Specialized LLM (your domain)
```

**When to fine-tune:**

| Scenario | Use Fine-tuning? | Alternative |
|----------|-----------------|-------------|
| Need specific writing style/tone | ✅ Yes | — |
| Domain-specific terminology | ✅ Yes | Few-shot prompting |
| Consistent output format | ✅ Yes | Structured output / prompt engineering |
| Answer from your documents | ❌ No | Use **RAG** instead |
| General Q&A | ❌ No | Use prompt engineering |
| Cost-sensitive (reduce tokens) | ✅ Yes (shorter prompts needed) | — |

**Fine-tuning vs RAG:**

| Aspect | Fine-tuning | RAG |
|--------|-----------|-----|
| Changes model weights | ✅ Yes | ❌ No |
| Needs training data | ✅ Yes (lots) | ❌ No (just documents) |
| Data freshness | Stale until retrained | Real-time (ingest new docs) |
| Cost | High (GPU training) | Low (API calls) |
| Best for | Style, format, domain language | Document Q&A, knowledge retrieval |

---

### Q16. What are foundation models?

**A:** **Foundation models** are large pre-trained models that serve as the base for many downstream tasks. They are trained on broad data and can be adapted to specific applications.

**Characteristics:**
- Trained on massive, diverse datasets.
- Can be adapted via fine-tuning, prompting, or RAG.
- One model, many tasks (text → translation, summarization, Q&A, code).

**Examples:**
| Model | Type | Foundation For |
|-------|------|----------------|
| GPT-4 | Text + Vision | ChatGPT, API applications |
| Gemini | Multimodal | Google products, SAP GenAI Hub |
| BERT | Text understanding | Search, classification |
| Stable Diffusion | Image generation | Art tools, design apps |
| Whisper | Speech-to-text | Transcription services |

**SAP context:** SAP GenAI Hub provides access to foundation models from multiple providers (OpenAI, Google, Meta) that can be used in SAP applications.

---

## 🔹 Section 4 — GenAI Architecture & Infrastructure

### Q17. What is an LLM API? How do you interact with LLMs programmatically?

**A:** An **LLM API** allows developers to send requests to an LLM and receive generated text responses.

```python
# Direct API call (Google Gemini)
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Explain quantum computing simply")
print(response.text)

# Using LangChain (abstraction layer)
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
response = llm.invoke("Explain quantum computing simply")
print(response.content)
```

**API components:**
- **Endpoint URL** — Where to send requests.
- **API Key** — Authentication.
- **Request body** — Prompt, parameters (temperature, max_tokens, etc.).
- **Response** — Generated text, usage statistics.

---

### Q18. What is model quantization?

**A:** **Quantization** reduces model size and speeds up inference by using lower-precision numbers for weights.

| Precision | Bits per Weight | Model Size (7B params) | Speed | Quality |
|-----------|----------------|----------------------|-------|---------|
| **FP32** (full) | 32 bits | 28 GB | Slowest | Best |
| **FP16** | 16 bits | 14 GB | Fast | Near-best |
| **INT8** | 8 bits | 7 GB | Faster | Slight loss |
| **INT4** | 4 bits | 3.5 GB | Fastest | Noticeable loss |

**Why quantize:**
- Run large models on consumer hardware (laptops, phones).
- Reduce API inference costs.
- Faster response times.

**Trade-off:** Lower precision = faster and smaller, but slightly lower quality outputs.

---

### Q19. What is inference vs. training?

**A:**

| Aspect | Training | Inference |
|--------|---------|-----------|
| **What** | Teaching the model | Using the trained model |
| **When** | Before deployment | After deployment |
| **Compute** | Very high (thousands of GPUs, weeks) | Low (single GPU, milliseconds) |
| **Cost** | Millions of dollars | Cents per request |
| **Data** | Massive training dataset | Single user input |
| **Output** | Model weights | Generated text/prediction |

**Analogy:**
- **Training** = A student studying for years.
- **Inference** = The student answering questions in an exam.

---

## 🔹 Section 5 — Responsible GenAI

### Q20. What are the ethical concerns with Generative AI?

**A:**

| Concern | Description | Mitigation |
|---------|------------|------------|
| **Hallucination** | Generates false but convincing information | RAG, fact-checking, source citation |
| **Bias** | Reflects biases in training data | Diverse training data, bias testing |
| **Misinformation** | Can generate fake news, deepfakes | Content watermarking, detection tools |
| **Copyright** | May reproduce copyrighted content | Filtering, attribution, legal compliance |
| **Privacy** | May leak personal data from training | Data anonymization, PII filtering |
| **Job displacement** | Automates knowledge work | Reskilling, human-AI collaboration |
| **Environmental impact** | Training requires massive energy | Efficient architectures, carbon offsets |

---

### Q21. What is AI alignment?

**A:** **AI alignment** ensures AI systems behave in ways that are consistent with human values and intentions.

**Key aspects:**
- **Helpfulness** — AI should assist users effectively.
- **Harmlessness** — AI should not produce harmful content.
- **Honesty** — AI should not deceive or generate false information.

**Alignment techniques:**
- **RLHF** — Train on human preferences.
- **Constitutional AI** — Define explicit rules the AI must follow.
- **Red-teaming** — Adversarial testing to find failure modes.
- **Guardrails** — Content filters, output validation.

---

### Q22. What are AI guardrails?

**A:** **Guardrails** are safety mechanisms that constrain AI behavior to prevent harmful, inappropriate, or incorrect outputs.

**Types:**
- **Input guardrails** — Filter harmful or malicious user inputs (prompt injection detection).
- **Output guardrails** — Filter inappropriate, biased, or harmful generated content.
- **Behavioral guardrails** — Limit what the AI can do (e.g., can't execute code, can't access external systems).
- **Content policies** — Define what topics the AI can/cannot discuss.

**Implementation:**

```python
# Simple output guardrail
def is_safe(response: str) -> bool:
    banned_topics = ["violence", "illegal", "harmful"]
    return not any(topic in response.lower() for topic in banned_topics)

result = llm.invoke(prompt)
if is_safe(result.content):
    return result.content
else:
    return "I cannot provide information on that topic."
```

---

## 🔹 Section 6 — Quick Fire Questions

### Q23. What is zero-shot, one-shot, and few-shot learning?

**A:**

| Type | Examples Given | How It Works |
|------|---------------|-------------|
| **Zero-shot** | None | Model performs task with just instructions |
| **One-shot** | 1 example | Model learns from a single example |
| **Few-shot** | 2-10 examples | Model learns from a few examples in the prompt |

```
# Zero-shot:
"Classify this review as positive or negative: 'Great product!'"

# One-shot:
"Classify reviews:
 'Loved it!' → Positive
 'Terrible experience' → ?"

# Few-shot:
"Classify reviews:
 'Loved it!' → Positive
 'Worst purchase ever' → Negative
 'Pretty good value' → Positive
 'Broke after a week' → ?"
```

---

### Q24. What is the difference between a chatbot, an assistant, and an agent?

**A:**

| Type | Capabilities | Autonomy | Example |
|------|-------------|----------|---------|
| **Chatbot** | Responds to messages | Low — follows scripts | Customer service chat |
| **Assistant** | Understands context, uses tools | Medium — follows instructions | Siri, Alexa, SAP Joule |
| **Agent** | Plans, reasons, acts autonomously | High — decides its own steps | Auto-GPT, LangGraph agents |

---

### Q25. What is multimodal AI?

**A:** **Multimodal AI** can process and generate **multiple types of data** — text, images, audio, video — in a single model.

| Model | Modalities |
|-------|-----------|
| GPT-4o | Text + images + audio |
| Gemini | Text + images + audio + video + code |
| Claude 3 | Text + images |
| DALL-E | Text → images |

**Example:** Upload an image of a chart → Ask "What trends does this chart show?" → Get a text analysis.

---

### Q26. What is the difference between Gemini and GPT?

**A:**

| Aspect | Gemini (Google) | GPT-4 (OpenAI) |
|--------|----------------|----------------|
| **Company** | Google DeepMind | OpenAI |
| **Architecture** | Transformer (multimodal native) | Transformer (text-first, vision added) |
| **Context window** | Up to 1M tokens | Up to 128K tokens |
| **Modalities** | Text, image, audio, video, code | Text, image, audio |
| **Open source** | Gemma (smaller variants) | No |
| **SAP integration** | ✅ Via GenAI Hub | ✅ Via GenAI Hub |
| **Pricing** | Competitive | Higher |

---

> **💡 Viva Tip:** GenAI questions will likely focus on **practical understanding** — what LLMs can/can't do, when to use RAG vs fine-tuning, hallucination prevention, and responsible AI practices. Show you understand both capabilities AND limitations.

---

*End of Unit 6 — Generative AI Fundamentals ✨*
