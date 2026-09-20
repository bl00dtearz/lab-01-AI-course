# Lab 01 — The Price of One Request

## 1. Prediction and measurement

The purpose of the lab is to see how the same task can require different numbers of tokens in English, Russian and Kazakh.

Before measuring tokens, I compared the texts by characters, UTF-8 bytes and words. For the prediction I used bytes, because the Russian and Kazakh texts take about twice as many bytes as English.

**Prediction for the complaint:**
- Russian / English ≈ **1.92×**
- Kazakh / English ≈ **2.13×**

The tokenizer is not required to follow characters, bytes or words, so this was only a hypothesis.

### Part 1 measurements

| Text | EN chars | RU chars | KK chars | EN bytes | RU bytes | KK bytes |
|---|---:|---:|---:|---:|---:|---:|
| Sentence | 69 | 75 | 72 | 69 | 139 | 135 |
| Complaint | 300 | 315 | 344 | 300 | 576 | 640 |
| System prompt | 175 | 181 | 206 | 175 | 331 | 380 |

### Prediction vs measured Gemini input

| Language | Prediction vs EN | Measured Gemini input | Difference |
|---|---:|---:|---|
| Russian | ≈ 1.92× | 1.30× (131 / 101) | lower than predicted |
| Kazakh | ≈ 2.13× | 2.35× (237 / 101) | slightly higher |

The measured result shows that token cost does not follow byte count exactly: tokenization depends on the language and the model's tokenizer.

## 2. Annual cost at a justified volume

I used **2,000 support requests per day (730,000 per year)** as a simple production-scale scenario for comparing the three languages.

| Language | Input tokens/request | Output tokens/request | Cost/request | Annual paid cost |
|---|---:|---:|---:|---:|
| English | 101 | 48 | $0.0003 | **$186.70** |
| Russian | 131 | 126 | $0.0006 | **$416.65** |
| Kazakh | 237 | 164 | $0.0008 | **$578.71** |

*Paid-price comparison uses $0.75 per 1M input tokens and $3.75 per 1M output tokens. The experiment itself was run on the Gemini Free Tier, so the actual API charge during the experiment was $0.*

## 3. Model for a Kazakh support queue

**Model: Gemini 3.8 Flash, provisionally.**

It is the model tested in this experiment and produced a Kazakh response without inventing an account number, rate or date when the required documents were missing. It also answered in Kazakh.

Its measured cost in this scenario is about **$0.0008 per request**.

Before production, I would validate it on a larger Kazakh support test set for accuracy, safety and consistency.

## 4. Cost lever not used

**Prompt caching** was not used in this lab; it could reduce the repeated input cost of the system prompt.

## 5. Conclusion

The main result is that text size and token count are related but not the same thing. In this corpus, Kazakh needs more tokens than English, and the difference depends strongly on the tokenizer.

Since API cost depends on input and output tokens, language and model choice can noticeably change the final bill.

## Declaration of AI use

I used **Claude and Gemini 3.8 Flash** during this lab. Claude was used to explain the laboratory instructions, adapt the original Anthropic-based code to the Gemini API, troubleshoot errors and check calculations. Gemini 3.8 Flash was used as the model under test in Part 2 to count tokens and generate support responses in English, Russian and Kazakh.

I ran the Python scripts locally, checked the resulting token counts and `measurements.json`, and used those measured values for the calculations. The API key was kept in `.env` and was not included in the repository. The submitted code and measurement file allow the experiment and calculations to be reproduced, and I can explain the measurements, ratios and cost calculation during the oral review.
