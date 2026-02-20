from trulens.core import Feedback
from trulens.core.feedback.selector import Selector
from trulens.otel.semconv.trace import SpanAttributes
import numpy as np

def groundedness_score(contexts, output):
    if not contexts or not output:
        return 0.0
    ctx = " ".join(contexts).lower()
    out = output.lower()
    return float(any(word in out for word in ctx.split()[:20]))

def relevance_score(question, answer):
    if not question or not answer:
        return 0.0
    return float(len(answer) > 10)

def context_relevance_score(question, contexts):
    if not contexts:
        return 0.0
    return 1.0

f_groundedness = Feedback(
    groundedness_score,
    name="Groundedness"
).on({
    "contexts": Selector(
        span_type=SpanAttributes.SpanType.RETRIEVAL,
        span_attribute=SpanAttributes.RETRIEVAL.RETRIEVED_CONTEXTS,
        collect_list=True,
    )
}).on({
    "output": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.OUTPUT,
    )
})

f_answer_relevance = Feedback(
    relevance_score,
    name="Answer Relevance"
).on({
    "question": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.INPUT,
    )
}).on({
    "answer": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.OUTPUT,
    )
})

f_context_relevance = Feedback(
    context_relevance_score,
    name="Context Relevance"
).on({
    "question": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.INPUT,
    )
}).on({
    "contexts": Selector(
        span_type=SpanAttributes.SpanType.RETRIEVAL,
        span_attribute=SpanAttributes.RETRIEVAL.RETRIEVED_CONTEXTS,
        collect_list=True,
    )
}).aggregate(np.mean)

feedbacks = [
    f_groundedness,
    f_answer_relevance,
    f_context_relevance,
]
