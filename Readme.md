

This project uses a multi-agent system built with `pyautogen` to automatically write, edit, and compile a complete fiction novel based on a single prompt.

## How to Use

1.  **Install Dependencies:**
    ```
    pip install pyautogen
    ```

2. **Configure settings:**
    This script is set to connect to a local OpenAI-compatible API server running at `http://localhost:1234/v1` which is the default for LM Studio. You can use tools like [LM Studio](https://lmstudio.ai/), [Ollama](https://ollama.com/), or any other OpenAI compatible endpoint, just change the url and add api key as nessecary. You can also set a target word count, number of chapters, etc. 

```
# --- Target for the final novel ---
TARGET_WORD_COUNT = 25000  # The script will stop once the novel exceeds this word count
MAX_CHAPTERS = 20          # A safety limit to prevent infinite loops
EDIT_CYCLE_CHAPTERS = 3    # Trigger the editing process every 3 chapters

# --- LLM Configuration ---
config_list_local = [
    {
        "model": "local-model",
        "base_url": "http://localhost:1234/v1",
        "api_key": "not-needed",
```

2.  **Set the prompt.**
Edit this section of the python script to your liking. 

```
# ======================================================================================
# MAIN WORKFLOW
# ======================================================================================
if __name__ == "__main__":
    print("="*80)
    print("🚀 STARTING FULL NOVEL GENERATION PROCESS WITH EDITOR...")
    print("="*80)

    # --- Initial Novel Idea ---
    novel_prompt_content = """
    Project Goal: Novel length work in the style of late twentieth century postmodern literary fiction. 
    Core Idea: In this playful and perplexing book, we meet a young Parisian researcher who lives inside his bathroom. As he sits in his tub meditating on existence (and refusing to tell us his name), the people around him--his girlfriend, Edmondsson, the Polish painters in his kitchen--each in their own way further enables his peculiar lifestyle, supporting his eccentric quest for immobility. But an invitation to the Austrian embassy shakes up his stable world, prompting him to take a risk and leave his bathroom . . .
    """

    # ======================================================================================
    # PHASE 1: ARCHITECTURE
    # ======================================================================================
```

4.  **Run the Script:**
    ```bash
    python write_novel.py
    ```

## Output

The script will generate all its files in the `project_files/` directory:
-   `plot_outline.txt`, `character_bible.txt`, `world_guide.txt`: The foundational documents.
-   `chapter_1.txt`, `chapter_2.txt`, etc.: The individual, edited chapters.
-   `complete_novel.txt`: The final, compiled manuscript.

