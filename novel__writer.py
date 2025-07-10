# write_novel.py

import autogen
import os
import json
import re

# ======================================================================================
# CONFIGURATION
# ======================================================================================
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
    }
]

llm_config = {
    "config_list": config_list_local,
    "cache_seed": None,  # Use a number for reproducible results, None for randomness
    "temperature": 0.75, # Slightly higher for more creative writing
}

# --- File and Directory Setup ---
OUTPUT_DIR = "project_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ======================================================================================
# AGENT DEFINITIONS
# ======================================================================================

# --- Architect Agent ---
architect = autogen.AssistantAgent(
    name="Architect",
    llm_config=llm_config,
    system_message="""You are the Architect. You create the blueprint for a novel. Based ONLY on the provided prompt, you must generate a plot outline, a character bible, and a world guide. Your response MUST be a single, valid JSON object with three keys: "plot_outline", "character_bible", and "world_guide". The value for each key MUST be a single string. Do not include any other text or explanations."""
)

# --- Novelist Agent ---
novelist = autogen.AssistantAgent(
    name="Novelist",
    llm_config=llm_config,
    system_message="""You are a fiction novelist. You write compelling, human-like prose.
- When writing a NEW chapter, you will be given a plot outline, character bible, world guide, and a summary of the previous chapter. Your task is to write the *next* chapter, keeping it consistent with all provided materials.
- When REVISING a chapter, you will be given the original chapter text and feedback from an editor. Your task is to rewrite the chapter, incorporating the editor's suggestions to improve it.
- Write ONLY the text of the chapter. Do NOT add titles like "Chapter X" or any other explanatory text.
"""
)

# --- Editor Agent (NEW) ---
editor = autogen.AssistantAgent(
    name="Editor",
    llm_config=llm_config,
    system_message="""You are a sharp, insightful book editor. You will be given the text of a novel chapter, along with the master plot, character, and world guides.
Your task is to provide specific, constructive feedback on the chapter.
Focus on:
- Pacing: Does the chapter move too quickly or too slowly?
- Consistency: Does it align with the established plot, character arcs, and world rules?
- Plot Holes: Are there any logical inconsistencies?
- Prose: Is the writing clear, engaging, and effective?
Provide a bulleted list of actionable suggestions for the novelist to use for revision. Do not rewrite the chapter yourself. Respond with ONLY the feedback.
"""
)

# --- Summarizer Agent ---
summarizer = autogen.AssistantAgent(
    name="Summarizer",
    llm_config=llm_config,
    system_message="""You are an expert summarizer. You will be given the text of a novel chapter. Create a concise summary of its key plot events, character developments, and any new information revealed. This summary will be used by the novelist for continuity, so it must be accurate and clear. Respond with ONLY the summary text."""
)

# --- User Proxy Agent ---
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "content" in msg and msg["content"] is not None and len(msg["content"].strip()) > 0,
    code_execution_config=False,
)


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
    print("\n--- PHASE 1: ARCHITECTURE ---")
    architecture_task = f"Here is the project prompt:\n---\n{novel_prompt_content}\n---\nGenerate the plot outline, character bible, and world guide."
    user_proxy.initiate_chat(architect, message=architecture_task, clear_history=True)

    try:
        response_content = user_proxy.last_message(architect).get("content", "")
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if not json_match: raise ValueError("No valid JSON object found in the Architect's response.")
        
        documents = json.loads(json_match.group(0))
        plot_outline = str(documents["plot_outline"])
        character_bible = str(documents["character_bible"])
        world_guide = str(documents["world_guide"])

        with open(f"{OUTPUT_DIR}/plot_outline.txt", "w", encoding='utf-8') as f: f.write(plot_outline)
        with open(f"{OUTPUT_DIR}/character_bible.txt", "w", encoding='utf-8') as f: f.write(character_bible)
        with open(f"{OUTPUT_DIR}/world_guide.txt", "w", encoding='utf-8') as f: f.write(world_guide)
        
        print("✅ Successfully created and saved foundational documents.")
        print("--- PHASE 1 COMPLETE ---\n")
    except Exception as e:
        print(f"\n🛑 ERROR in Phase 1: {e}")
        exit()

    # ======================================================================================
    # PHASE 2: ITERATIVE CHAPTER WRITING & EDITING
    # ======================================================================================
    print("--- PHASE 2: WRITING THE NOVEL ---")
    
    chapter_number = 1
    total_word_count = 0
    # Use a dictionary to store summaries, with the chapter number as the key.
    chapter_summaries = {0: "This is the beginning of the novel. The first chapter should set the scene and introduce the main character and the initial incident."}
    
    while total_word_count < TARGET_WORD_COUNT and chapter_number <= MAX_CHAPTERS:
        print(f"\n-- Writing Chapter {chapter_number} --")
        
        # 1. Write the next chapter
        writing_task = f"PLOT: {plot_outline}\n\nCHARACTERS: {character_bible}\n\nWORLD: {world_guide}\n\nSUMMARY OF PREVIOUS CHAPTER: {chapter_summaries[chapter_number - 1]}\n\nTASK: Write Chapter {chapter_number} of the novel."
        user_proxy.initiate_chat(novelist, message=writing_task, clear_history=True)
        new_chapter_content = user_proxy.last_message(novelist).get("content", "").strip()
        
        if not new_chapter_content:
            print(f"🛑 ERROR: Novelist returned empty response for Chapter {chapter_number}. Aborting."); break
            
        with open(f"{OUTPUT_DIR}/chapter_{chapter_number}.txt", "w", encoding='utf-8') as f: f.write(new_chapter_content)
        print(f"✅ Chapter {chapter_number} (draft) written and saved.")
        
        # 2. Summarize the new chapter
        summary_task = f"Summarize this chapter:\n\n{new_chapter_content}"
        user_proxy.initiate_chat(summarizer, message=summary_task, clear_history=True)
        chapter_summaries[chapter_number] = user_proxy.last_message(summarizer).get("content", "").strip()
        
        # 3. Trigger Editing Cycle every N chapters
        if chapter_number > 0 and chapter_number % EDIT_CYCLE_CHAPTERS == 0:
            print(f"\n--- TRIGGERING EDITING CYCLE FOR CHAPTERS {chapter_number - EDIT_CYCLE_CHAPTERS + 1}-{chapter_number} ---")
            for i in range(chapter_number - EDIT_CYCLE_CHAPTERS + 1, chapter_number + 1):
                print(f"\n-- Editing Chapter {i} --")
                
                # a. Load the chapter draft
                with open(f"{OUTPUT_DIR}/chapter_{i}.txt", "r", encoding='utf-8') as f: chapter_to_edit = f.read()
                
                # b. Editor provides feedback
                editing_task = f"PLOT: {plot_outline}\n\nCHARACTERS: {character_bible}\n\nWORLD: {world_guide}\n\nCHAPTER {i} TEXT:\n{chapter_to_edit}\n\nTASK: Provide a bulleted list of actionable feedback for the novelist."
                user_proxy.initiate_chat(editor, message=editing_task, clear_history=True)
                editor_feedback = user_proxy.last_message(editor).get("content", "").strip()
                print(f"   - Editor Feedback for Chapter {i}:\n{editor_feedback}")
                
                # c. Novelist revises the chapter
                revision_task = f"ORIGINAL CHAPTER {i}:\n{chapter_to_edit}\n\nEDITOR'S FEEDBACK:\n{editor_feedback}\n\nTASK: Rewrite the chapter, incorporating the editor's feedback to improve it."
                user_proxy.initiate_chat(novelist, message=revision_task, clear_history=True)
                revised_chapter_content = user_proxy.last_message(novelist).get("content", "").strip()

                # d. Save the revised chapter
                with open(f"{OUTPUT_DIR}/chapter_{i}.txt", "w", encoding='utf-8') as f: f.write(revised_chapter_content)
                print(f"✅ Chapter {i} revised and saved.")

                # e. Re-summarize the *edited* chapter for future continuity
                resummary_task = f"Summarize this REVISED chapter:\n\n{revised_chapter_content}"
                user_proxy.initiate_chat(summarizer, message=resummary_task, clear_history=True)
                chapter_summaries[i] = user_proxy.last_message(summarizer).get("content", "").strip()
                print(f"   - Summary for Chapter {i} updated.")

        # 4. Update total word count after all edits for the batch are done
        current_word_count = 0
        for i in range(1, chapter_number + 1):
            with open(f"{OUTPUT_DIR}/chapter_{i}.txt", "r", encoding='utf-8') as f:
                current_word_count += len(f.read().split())
        total_word_count = current_word_count
        print(f"\n   - Total words so far: {total_word_count} / {TARGET_WORD_COUNT}")

        chapter_number += 1

    print("\n--- PHASE 2 COMPLETE ---\n")
    
    # ======================================================================================
    # PHASE 3: FINAL COMPILATION
    # ======================================================================================
    print("--- PHASE 3: COMPILING THE NOVEL ---")
    try:
        final_novel_content = []
        # Loop up to the last chapter written (chapter_number - 1)
        for i in range(1, chapter_number):
            chapter_filename = f"{OUTPUT_DIR}/chapter_{i}.txt"
            if os.path.exists(chapter_filename):
                with open(chapter_filename, "r", encoding='utf-8') as f:
                    final_novel_content.append(f"--- CHAPTER {i} ---\n\n{f.read()}\n\n")
        
        with open(f"{OUTPUT_DIR}/complete_novel.txt", "w", encoding='utf-8') as f:
            f.write("".join(final_novel_content))
        print(f"✅ Novel compiled successfully into 'complete_novel.txt' with {total_word_count} words.")
    except Exception as e:
        print(f"🛑 ERROR in Phase 3: Could not compile the final novel. {e}")

    print("\n="*80)
    print("✅ FULL NOVEL GENERATION PROCESS FINISHED!")
    print("="*80)
