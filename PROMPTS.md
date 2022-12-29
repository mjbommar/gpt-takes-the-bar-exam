# Prompt Styles

### Single choice only
```
Imagine you are answering a Bar Exam question related to {row["question_category"]}. 
Please respond with this format:
Answer: <CHOICE> 

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

### Single choice and explanation
```
Imagine you are answering a Bar Exam question related to {row["question_category"]}. 
Please respond with this format:
Answer: <CHOICE> 
Reason: <EXPLANATION>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

### Top two choices only
```
Imagine you are answering a Bar Exam question related to {row["question_category"]}. 
Please respond with this format:
Answer: <CHOICE> 
Backup Answer: <NEXT MOST LIKELY CHOICE>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

### Top two choices and explanation
```
Imagine you are answering a Bar Exam question related to {row["question_category"]}. 
Please respond with this format:
Answer: <CHOICE> 
Backup Answer: <NEXT MOST LIKELY CHOICE>
Reason: <EXPLANATION>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

### Top two choices and re-prompt
 * Initial Prompt
```
Please answer the following Bar Exam question in the following format:  
First Choice: <CHOICE> 
Second Choice: <NEXT MOST LIKELY CHOICE>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

* Re-prompt
```
Please answer the following Bar Exam question in the following format:  
Choice: <CHOICE> 

Question: {question_text}
(A) {row["first_choice"].strip()}
(B) {row["second_choice"].strip()}
```


### Rank order all choices
```
Please answer the following Bar Exam question in the following rank order format: 
First Choice: <LETTER>
Second Choice: <LETTER>
Third Choice: <LETTER>
Fourth Choice: <LETTER>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```

### Rank order top three choices
```
Please answer the following Bar Exam question in the following rank order format: 
First Choice: <LETTER>
Second Choice: <LETTER>
Third Choice: <LETTER>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}
```
