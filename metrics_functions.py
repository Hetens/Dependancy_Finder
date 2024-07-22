import numpy as np
from rouge_score import rouge_scorer
import pandas as pd
import nltk
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE
from nltk.lm.models import Laplace
import re
#accuracy and response time is periodically updated in the dataset for 10
nltk.download('punkt')
def compute_bleu(reference, candidate):
    reference = reference.split()
    candidate = candidate.split()
    reference_length = len(reference)
    candidate_length = len(candidate)

    if candidate_length == 0:
        return 0.0

    matches = sum(1 for word in candidate if word in reference)
    precision = matches / candidate_length

    brevity_penalty = np.exp(1 - reference_length / candidate_length) if candidate_length < reference_length else 1.0

    return brevity_penalty * precision

def compute_rouge(reference, candidate):
    scorer = rouge_scorer.RougeScorer([ 'rouge1','rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    return scores['rougeL'].fmeasure  

def compute_perplexity(reference, candidate, n=3):
    # Tokenize and lowercase the reference text
    tokenized_reference = list(map(str.lower, nltk.word_tokenize(reference)))
    
    # Prepare the training data
    train_data, padded_vocab = padded_everygram_pipeline(n, [tokenized_reference])
    
    # Train the language model with Laplace smoothing
    model = Laplace(n)  # Use Laplace smoothing instead of MLE
    model.fit(train_data, padded_vocab)
    
    # Tokenize and lowercase the candidate text
    tokenized_candidate = list(map(str.lower, nltk.word_tokenize(candidate)))
    
    # Prepare the test data
    test_data, _ = padded_everygram_pipeline(n, [tokenized_candidate])
    
    # Compute perplexity for the entire candidate text
    try:
        perplexity = model.perplexity(next(test_data))
        return perplexity
    except ValueError as e:
        print(f"Error in perplexity calculation: {e}")
        return None

def analyze_ngrams(reference, candidate, n=3):
    # Tokenize and lowercase the texts
    tokenized_reference = list(map(str.lower, nltk.word_tokenize(reference)))
    tokenized_candidate = list(map(str.lower, nltk.word_tokenize(candidate)))
    
    # Prepare the training data and train the model
    train_data, padded_vocab = padded_everygram_pipeline(n, [tokenized_reference])
    model = Laplace(n)
    model.fit(train_data, padded_vocab)
    
    # Analyze n-grams in the candidate text
    ngrams = list(nltk.ngrams(tokenized_candidate, n))
    unseen_ngrams = []
    low_prob_ngrams = []
    
    for ngram in ngrams:
        prob = model.score(ngram[-1], ngram[:-1])
        if prob == 0:
            unseen_ngrams.append(ngram)
        elif prob < 0.01:  # Arbitrary threshold for "low probability"
            low_prob_ngrams.append((ngram, prob))
    
    return unseen_ngrams, low_prob_ngrams

def content_overlap_score(prompt, response):
    prompt_words = set(re.findall(r'\w+', prompt.lower()))
    response_words = set(re.findall(r'\w+', response.lower()))
    overlap = len(prompt_words.intersection(response_words))
    return overlap / len(prompt_words) if prompt_words else 0

def improved_semantic_coherence(response):
    sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]
    if len(sentences) < 2:
        return 0
    
    word_sets = [set(re.findall(r'\w+', s.lower())) for s in sentences]
    coherence_scores = []
    
    for i in range(len(word_sets) - 1):
        overlap = len(word_sets[i].intersection(word_sets[i+1]))
        union = len(word_sets[i].union(word_sets[i+1]))
        coherence_scores.append(overlap / union if union else 0)
    
    # Penalize responses with too few or too many sentences
    length_penalty = 1 - abs(0.5 - (len(sentences) / 10))
    
    return (sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0) * length_penalty

def factual_consistency(prompt, response):
    prompt_facts = set(re.findall(r'\b\w+\b', prompt.lower()))
    response_facts = set(re.findall(r'\b\w+\b', response.lower()))
    
    consistent_facts = prompt_facts.intersection(response_facts)
    inconsistent_facts = response_facts - prompt_facts
    
    consistency_score = len(consistent_facts) / (len(consistent_facts) + len(inconsistent_facts))
    return consistency_score
