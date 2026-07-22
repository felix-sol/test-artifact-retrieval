import tiktoken
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from artifact_retrieval.ingestion.data_ingestion.config.data_ingestion_config import FEATURE_ROOT, STORY_ROOT, INLINE_JBEHAVE_ROOT



def count_tokens_per_document(file_root: Path, model_name: str = "text-embedding-3-large") -> list[int]:
    token_count = [] 

    for source in file_root.rglob("*"):
        if source.is_file():
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
                encoding = tiktoken.encoding_for_model(model_name)
                num_tokens = len(encoding.encode(content))
                token_count.append(num_tokens)


    return token_count

def plot_histogram_for_tokens(token_count: list[int], name: str):
    token_arr = np.array(token_count)

    threshold = 4000 # not much data above 4000 Tokens
    bin_width = 250

    regular_data = [x for x in token_arr if x <= threshold]
    overflow_count = sum(x > threshold for x in token_arr)

    bins = np.arange(0, threshold + bin_width, bin_width)
    counts, edges = np.histogram(regular_data, bins=bins)

    # append Overflow-Bucket 
    counts = np.append(counts, overflow_count)
    edges = np.append(edges, threshold + bin_width)

    plt.bar(edges[:-1], counts, width=bin_width, align='edge', edgecolor='blue')
    plt.xlabel("Number of Tokens")
    plt.ylabel("Frequency")
    plt.title(f"Histogram of Tokens in {name}")

    xticks = list(range(0, threshold + 1, 1000)) + [threshold + bin_width]
    xticklabels = [str(x) for x in range(0, threshold + 1, 1000)] + [f">{threshold}"]
    plt.xticks(xticks, xticklabels)
    plt.show()



def plot_histogram_for_all_files(feature_token_count: list[int], story_token_count: list[int], inline_jbehave_token_count: list[int]):
    all_tokens = feature_token_count + story_token_count + inline_jbehave_token_count
    plot_histogram_for_tokens(all_tokens, "all input Files ")


def get_name_of_file_with_most_tokens(token_count: list[int], file_root: Path) -> str:
    max_tokens = max(token_count)
    index_of_max = token_count.index(max_tokens)
    file_with_most_tokens = list(file_root.rglob("*"))[index_of_max]
    return file_with_most_tokens.name

def calculate_token_price(token_count: list[int], price_per_1000_tokens: float = 0.000123) -> float:
    total_tokens = sum(token_count)
    total_price = (total_tokens / 1000) * price_per_1000_tokens
    return total_price

feature_list = count_tokens_per_document(FEATURE_ROOT)
story_list = count_tokens_per_document(STORY_ROOT)
inline_jbehave_list = count_tokens_per_document(INLINE_JBEHAVE_ROOT)

# histograms for each file type
#plot_histogram_for_tokens(feature_list, FEATURE_ROOT.name)
#plot_histogram_for_tokens(story_list, STORY_ROOT.name)
#plot_histogram_for_tokens(inline_jbehave_list, INLINE_JBEHAVE_ROOT.name)

# distribution of all files together
plot_histogram_for_all_files(feature_list, story_list, inline_jbehave_list)

# calculate total tokens and embedding run price
total_token_feature_files = sum(feature_list)
total_token_story_files = sum(story_list)
total_token_inline_jbehave_files = sum(inline_jbehave_list)
total_tokens_to_embed = total_token_feature_files + total_token_story_files + total_token_inline_jbehave_files
total_embedding_run_price = calculate_token_price(feature_list) + calculate_token_price(story_list) + calculate_token_price(inline_jbehave_list)

print(f"Number of tokens in {FEATURE_ROOT.name}: {total_token_feature_files}")
print(f"Number of tokens in {STORY_ROOT.name}: {total_token_story_files}")
print(f"Number of tokens in {INLINE_JBEHAVE_ROOT.name}: {total_token_inline_jbehave_files}")
print(f"Total number of tokens to embed: {total_tokens_to_embed}")
print(f"Total embedding run price: {total_embedding_run_price:.6f}€")

# find file with most tokens
max_feature_file = get_name_of_file_with_most_tokens(feature_list, FEATURE_ROOT)
max_story_file = get_name_of_file_with_most_tokens(story_list, STORY_ROOT)
max_inline_jbehave_file = get_name_of_file_with_most_tokens(inline_jbehave_list, INLINE_JBEHAVE_ROOT)

print(f"File with most tokens in {FEATURE_ROOT.name}: {max_feature_file} with {max(feature_list)} tokens")
print(f"File with most tokens in {STORY_ROOT.name}: {max_story_file} with {max(story_list)} tokens")
print(f"File with most tokens in {INLINE_JBEHAVE_ROOT.name}: {max_inline_jbehave_file} with {max(inline_jbehave_list)} tokens")

