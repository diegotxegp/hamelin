"""
Setting labels
~~~~~~~~~~~~~~

Plain-language names and explanations for Ludwig config keys, used when two
models' configurations are compared (Evaluation page > Compare). Kept free
of any Qt import so it can be used and tested anywhere.
"""

SETTING_INFO = {
    "batch_size": ("Batch Size", "How many examples the model looks at together before updating what it has learned. Smaller values update more often but can be noisier; larger values are steadier but need more memory."),
    "eval_batch_size": ("Evaluation Batch Size", "Like Batch Size, but only used while measuring performance, not while learning - so it doesn't affect training itself."),
    "effective_batch_size": ("Effective Batch Size", "The real batch size actually used once other settings are taken into account."),
    "epochs": ("Epoch Size", "How many times the model goes through the entire training dataset. More epochs means more learning, but too many can cause it to memorize instead of generalize."),
    "learning_rate": ("Learning Rate", "How big a step the model takes each time it updates what it has learned. Too high and it can overshoot; too low and training is very slow."),
    "dropout": ("Dropout", "Randomly ignores part of the model during training so it doesn't rely too heavily on any single detail. Helps prevent overfitting."),
    "early_stop": ("Early Stop Patience", "How many rounds without improvement the model tolerates before training is stopped early, to avoid wasting time once it has stopped getting better."),
    "validation_metric": ("Validation Metric", "The measurement used to decide whether the model is improving during training (e.g. accuracy or loss)."),
    "validation_field": ("Validation Field", "Which output the model is checked against to measure its progress during training."),
    "regularization_lambda": ("Regularization Strength", "How strongly the model is discouraged from becoming overly complex, which helps it generalize instead of memorizing the training data."),
    "regularization_type": ("Regularization Type", "The mathematical method used to discourage the model from becoming overly complex."),
    "weight_decay": ("Weight Decay", "A gentle penalty applied during training to keep the model's internal values small, which helps prevent overfitting."),
    "activation": ("Activation Function", "The mathematical function that decides how a layer's output responds to its input. Different choices change how the model learns patterns."),
    "num_fc_layers": ("Number of Layers", "How many extra processing layers the model uses in this part of the network."),
    "output_size": ("Output Size", "The number of values this part of the model produces to pass on to the next step."),
    "embedding_size": ("Embedding Size", "The size of the internal representation the model uses to capture the meaning of each input (like a word)."),
    "num_filters": ("Number of Filters", "How many different patterns this part of the model looks for at once."),
    "filter_size": ("Filter Size", "How large a chunk of the input the model looks at in one go when searching for patterns."),
    "pool_function": ("Pooling Method", "How the model condenses information after scanning for patterns (e.g. taking the maximum or average)."),
    "max_sequence_length": ("Max Sequence Length", "The longest input the model will read; anything beyond this length gets cut off."),
    "most_common": ("Vocabulary Size", "How many of the most frequent values (e.g. words) the model keeps track of; anything rarer gets grouped together."),
    "lowercase": ("Lowercase Text", "Whether text is converted to lowercase before the model reads it, so it doesn't treat \"Cat\" and \"cat\" as different things."),
    "tokenizer": ("Tokenizer", "The method used to split text into smaller pieces the model can understand."),
    "missing_value_strategy": ("Missing Value Strategy", "What the model does when a piece of data is missing (e.g. fill it in, or drop that row)."),
    "should_shuffle": ("Shuffle Data", "Whether the training data is mixed up in a random order before each epoch, which usually helps the model learn better."),
    "use_mixed_precision": ("Mixed Precision", "Whether the model uses a faster, lower-precision number format during training to speed things up."),
    "num_classes": ("Number of Classes", "How many different categories the model is choosing between."),
    "top_k": ("Top K", "How many of the model's best guesses are considered correct when measuring accuracy."),
    "reduce_input": ("Input Reduction", "How the model combines multiple pieces of input into a single summary before using them."),
    "reduce_output": ("Output Reduction", "How the model combines its internal results into the final output."),
    "learning_rate_scaling": ("Learning Rate Scaling", "How the Learning Rate is automatically adjusted based on the batch size."),
    "decay_rate": ("Decay Rate", "How quickly the Learning Rate shrinks over time during training."),
    "warmup_fraction": ("Warmup Fraction", "The portion of training spent gradually ramping the Learning Rate up from a small value, to stabilize early training."),
    "clipnorm": ("Gradient Clip (Norm)", "A safety limit that stops the model's updates from becoming too large all at once, which helps keep training stable."),
    "clipvalue": ("Gradient Clip (Value)", "A safety limit on the size of any single update during training, to keep learning stable."),
    "clipglobalnorm": ("Gradient Clip (Global Norm)", "A safety limit on the overall size of all updates combined during training, to keep learning stable."),
    "optimizer.type": ("Optimizer", "The algorithm the model uses to update itself as it learns from its mistakes."),
    "combiner.type": ("Combiner Type", "The method used to merge information from all inputs before making a prediction."),
    "split.type": ("Data Split Method", "How the dataset is divided into training, validation, and test portions."),
    "learning_rate_scheduler.decay": ("Learning Rate Schedule", "The pattern used to gradually change the Learning Rate over the course of training."),
}

_GENERIC_EXPLANATION = (
    "A more technical training setting - the exact value matters less than "
    "whether it's the same or different between the two runs."
)


def humanize_key(key):
    """Fallback display name for any setting not in SETTING_INFO: turns
    "trainer.some_setting" into "Some Setting", using the parent segment
    instead of a bare list index (".0") so it stays readable."""
    parts = key.split(".")
    last = parts[-1]
    index = None
    if last.isdigit() and len(parts) >= 2:
        index = int(last) + 1
        last = parts[-2]

    label = " ".join(w.capitalize() for w in last.replace("_", " ").split())
    return f"{label} #{index}" if index is not None else label


def _lookup_setting(key):
    parts = key.split(".")
    two = ".".join(parts[-2:]) if len(parts) >= 2 else None
    return SETTING_INFO.get(two) or SETTING_INFO.get(parts[-1])


def friendly_label(key):
    info = _lookup_setting(key)
    return info[0] if info else humanize_key(key)


def setting_explanation(key):
    info = _lookup_setting(key)
    return info[1] if info else _GENERIC_EXPLANATION
