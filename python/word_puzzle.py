import random
import tkinter as tk
from tkinter import messagebox, font
import winsound
import json
import os


class Stats:
    """Track game statistics."""
    
    def __init__(self, stats_file="word_puzzle_stats.json"):
        self.stats_file = stats_file
        self.wins = 0
        self.losses = 0
        self.streak = 0
        self.load()
    
    def load(self):
        """Load stats from file."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.wins = data.get('wins', 0)
                    self.losses = data.get('losses', 0)
                    self.streak = data.get('streak', 0)
            except:
                pass
    
    def save(self):
        """Save stats to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump({'wins': self.wins, 'losses': self.losses, 'streak': self.streak}, f)
        except:
            pass
    
    def win(self):
        """Record a win."""
        self.wins += 1
        self.streak += 1
        self.save()
    
    def lose(self):
        """Record a loss."""
        self.losses += 1
        self.streak = 0
        self.save()
    
    def get_summary(self):
        """Get stats summary."""
        return f"W: {self.wins} | L: {self.losses} | Streak: {self.streak}🔥"


class WordGame:
    """Pure logic for Hangman game."""
    
    # ASCII Hangman stages (0-6 wrong guesses)
    HANGMAN_STAGES = [
        # Stage 0: Empty gallows
        """
           ------
           |    |
           |
           |
           |
           |
        --------""",
        # Stage 1: Head
        """
           ------
           |    |
           |    O
           |
           |
           |
        --------""",
        # Stage 2: Body
        """
           ------
           |    |
           |    O
           |    |
           |
           |
        --------""",
        # Stage 3: Left arm
        """
           ------
           |    |
           |    O
           |   \|
           |
           |
        --------""",
        # Stage 4: Right arm
        """
           ------
           |    |
           |    O
           |   \|/
           |
           |
        --------""",
        # Stage 5: Left leg
        """
           ------
           |    |
           |    O
           |   \|/
           |   /
           |
        --------""",
        # Stage 6: Right leg (game over)
        """
           ------
           |    |
           |    O
           |   \|/
           |   / \\
           |
        --------"""
    ]
    
    # Categorized word list with hints
    WORD_CATEGORIES = {
        "🖥️ Tech": ["python", "computer", "programming", "algorithm", "function", "variable", 
                    "database", "network", "interface", "developer", "software", "hardware", 
                    "keyboard", "monitor", "internet", "server", "client", "protocol", "security"],
        "🎮 Gaming": ["challenge", "victory", "defeat", "strategy", "puzzle", "hangman"],
        "🧠 Mind": ["imagination", "creativity", "adventure", "discovery", "knowledge", "thinking"]
    }
    
    DIFFICULTY = {
        "Easy": 8,
        "Medium": 6,
        "Hard": 4
    }
    
    def __init__(self):
        self.word = None
        self.category = None
        self.guessed_letters = set()
        self.wrong_guesses = set()
        self.max_attempts = 6
        self.difficulty = "Medium"
        self.game_over = False
        self.won = False
    
    def new_game(self, difficulty="Medium"):
        """Start a fresh game with selected difficulty."""
        self.difficulty = difficulty
        self.max_attempts = self.DIFFICULTY[difficulty]
        
        # Pick random category and word
        self.category = random.choice(list(self.WORD_CATEGORIES.keys()))
        self.word = random.choice(self.WORD_CATEGORIES[self.category]).upper()
        
        self.guessed_letters = set()
        self.wrong_guesses = set()
        self.game_over = False
        self.won = False
    
    def guess(self, letter):
        """
        Process a letter guess.
        Returns: "correct", "wrong", "win", "lose", "already", "invalid"
        """
        letter = letter.upper().strip()
        
        # Validation
        if not letter or len(letter) != 1 or not letter.isalpha():
            return "invalid"
        
        if letter in self.guessed_letters or letter in self.wrong_guesses:
            return "already"
        
        # Record guess
        if letter in self.word:
            self.guessed_letters.add(letter)
            result = "correct"
        else:
            self.wrong_guesses.add(letter)
            result = "wrong"
        
        # Check win/lose
        if self._check_win():
            self.game_over = True
            self.won = True
            return "win"
        
        if self._check_lose():
            self.game_over = True
            self.won = False
            return "lose"
        
        return result
    
    def _check_win(self):
        """Check if all letters in the word have been guessed."""
        return all(letter in self.guessed_letters for letter in self.word)
    
    def _check_lose(self):
        """Check if too many wrong guesses."""
        return len(self.wrong_guesses) >= self.max_attempts
    
    @property
    def display_word(self):
        """Return word with unguessed letters as underscores."""
        return " ".join(
            letter if letter in self.guessed_letters else "_"
            for letter in self.word
        )
    
    @property
    def attempts_left(self):
        """Return number of remaining attempts."""
        return self.max_attempts - len(self.wrong_guesses)
    
    @property
    def hangman_stage(self):
        """Return current ASCII hangman drawing."""
        stage_index = min(len(self.wrong_guesses), len(self.HANGMAN_STAGES) - 1)
        return self.HANGMAN_STAGES[stage_index]
    
    def get_wrong_letters(self):
        """Return comma-separated list of wrong guesses."""
        return ", ".join(sorted(self.wrong_guesses)) if self.wrong_guesses else "None"


class App:
    """Modern Tkinter UI for Word Puzzle game."""
    
    # Colors
    BG_PRIMARY = "#1a1a1a"
    BG_SECONDARY = "#2d2d2d"
    FG_PRIMARY = "#ffffff"
    FG_ACCENT = "#00d4ff"
    COLOR_SUCCESS = "#00ff88"
    COLOR_ERROR = "#ff4466"
    COLOR_WARNING = "#ffaa00"
    
    # Encouragement messages
    ENCOURAGEMENTS = [
        "🎮 Ready to play? Guess the word!",
        "🧠 Think fast! Can you solve it?",
        "⚡ You got this! Start guessing!",
        "🎯 Challenge accepted! Let's go!",
        "🌟 Show me your word power!",
        "💪 Time to test your skills!",
        "🚀 Let's find that word together!",
        "🎪 The puzzle awaits... guess away!",
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("Word Puzzle")
        self.root.geometry("900x750")
        self.root.config(bg=self.BG_PRIMARY)
        self.root.resizable(False, False)
        
        # Configure styles
        self._configure_styles()
        
        self.game = WordGame()
        self.stats = Stats()
        self.current_encouragement_index = 0
        self._build_ui()
        self._start_new_game()
    
    def _configure_styles(self):
        """Configure fonts and colors."""
        self.font_title = font.Font(family="Segoe UI", size=32, weight="bold")
        self.font_large = font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_normal = font.Font(family="Segoe UI", size=11)
        self.font_mono = font.Font(family="Courier New", size=13)
        self.font_encourage = font.Font(family="Segoe UI", size=14, weight="bold")
    
    def _build_ui(self):
        """Construct all widgets with modern design."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(
            main_frame, text="🎮 WORD PUZZLE 🎮", font=self.font_title,
            fg=self.FG_ACCENT, bg=self.BG_PRIMARY
        )
        title_label.pack(pady=5)
        
        # Stats display
        self.stats_label = tk.Label(
            main_frame, text=self.stats.get_summary(), font=self.font_normal,
            fg=self.COLOR_SUCCESS, bg=self.BG_PRIMARY
        )
        self.stats_label.pack(pady=2)
        
        # Encouragement message
        self.encouragement_label = tk.Label(
            main_frame, text="", font=self.font_encourage,
            fg=self.COLOR_SUCCESS, bg=self.BG_PRIMARY, height=1
        )
        self.encouragement_label.pack(pady=5)
        
        # Difficulty selector
        difficulty_frame = tk.Frame(main_frame, bg=self.BG_SECONDARY)
        difficulty_frame.pack(fill="x", pady=5)
        
        tk.Label(difficulty_frame, text="Difficulty:", font=self.font_normal,
                fg=self.FG_PRIMARY, bg=self.BG_SECONDARY).pack(side="left", padx=10, pady=5)
        
        self.difficulty_var = tk.StringVar(value="Medium")
        for level in ["Easy", "Medium", "Hard"]:
            rb = tk.Radiobutton(
                difficulty_frame, text=level, variable=self.difficulty_var,
                value=level, command=self._on_difficulty_change, font=self.font_normal,
                fg=self.FG_PRIMARY, bg=self.BG_SECONDARY, activebackground=self.BG_SECONDARY,
                activeforeground=self.FG_ACCENT, selectcolor=self.BG_SECONDARY
            )
            rb.pack(side="left", padx=10)
        
        # Content area (split: hangman + word)
        content_frame = tk.Frame(main_frame, bg=self.BG_PRIMARY)
        content_frame.pack(fill="both", expand=False, pady=10)
        
        # Left: Hangman drawing
        hangman_frame = tk.Frame(content_frame, bg=self.BG_SECONDARY)
        hangman_frame.pack(side="left", padx=5, fill="both", expand=False)
        
        tk.Label(hangman_frame, text="🎭 Hangman", font=self.font_large,
                fg=self.FG_ACCENT, bg=self.BG_SECONDARY).pack(pady=3)
        
        self.hangman_label = tk.Label(
            hangman_frame, text="", font=("Courier New", 9), fg="#ff6688",
            bg=self.BG_SECONDARY, justify="left", width=35
        )
        self.hangman_label.pack(pady=5)
        
        # Right: Word display
        word_frame = tk.Frame(content_frame, bg=self.BG_SECONDARY)
        word_frame.pack(side="right", padx=5, fill="both", expand=False)
        
        tk.Label(word_frame, text="🎯 Word to Guess", font=self.font_large,
                fg=self.FG_ACCENT, bg=self.BG_SECONDARY).pack(pady=3)
        
        # Category hint
        self.category_label = tk.Label(
            word_frame, text="", font=self.font_normal, fg=self.FG_ACCENT,
            bg=self.BG_SECONDARY
        )
        self.category_label.pack(pady=2)
        
        self.display_label = tk.Label(
            word_frame, text="", font=("Courier New", 24, "bold"),
            fg=self.FG_ACCENT, bg=self.BG_SECONDARY
        )
        self.display_label.pack(pady=10)
        
        # Wrong guesses display
        tk.Label(word_frame, text="❌ Wrong Guesses:", font=self.font_normal,
                fg=self.FG_PRIMARY, bg=self.BG_SECONDARY).pack(pady=(5, 2))
        
        self.wrong_label = tk.Label(
            word_frame, text="", font=self.font_normal, fg=self.COLOR_ERROR,
            bg=self.BG_SECONDARY
        )
        self.wrong_label.pack(pady=2)
        
        # Attempts left
        attempts_frame = tk.Frame(word_frame, bg=self.BG_SECONDARY)
        attempts_frame.pack(pady=5)
        
        tk.Label(attempts_frame, text="❤️ Attempts:", font=self.font_normal,
                fg=self.FG_PRIMARY, bg=self.BG_SECONDARY).pack(side="left", padx=3)
        
        self.attempts_label = tk.Label(
            attempts_frame, text="", font=self.font_normal, fg=self.COLOR_SUCCESS,
            bg=self.BG_SECONDARY
        )
        self.attempts_label.pack(side="left", padx=3)
        
        # Message area
        self.message_label = tk.Label(
            main_frame, text="", font=self.font_normal,
            fg=self.FG_PRIMARY, bg=self.BG_PRIMARY, wraplength=850
        )
        self.message_label.pack(pady=5, fill="x")
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.BG_SECONDARY, height=50)
        input_frame.pack(fill="x", pady=8, padx=5)
        input_frame.pack_propagate(False)
        
        input_label = tk.Label(input_frame, text="💬 Type a letter and press Enter:", font=self.font_normal,
                fg=self.FG_PRIMARY, bg=self.BG_SECONDARY)
        input_label.pack(side="left", padx=10, pady=5)
        
        self.entry = tk.Entry(input_frame, font=("Segoe UI", 20, "bold"), width=3,
                             bg=self.BG_PRIMARY, fg=self.FG_ACCENT, insertbackground=self.FG_ACCENT,
                             bd=3, relief="solid")
        self.entry.pack(side="left", padx=10, pady=5)
        self.entry.bind("<Return>", lambda e: self._on_submit())
        
        submit_btn = tk.Button(
            input_frame, text="✓ Submit", command=self._on_submit, font=self.font_normal,
            bg=self.FG_ACCENT, fg=self.BG_PRIMARY, activebackground="#00d4ff",
            activeforeground=self.BG_PRIMARY, padx=15, pady=5, border=0
        )
        submit_btn.pack(side="left", padx=5)
        
        # Action buttons frame
        action_frame = tk.Frame(main_frame, bg=self.BG_PRIMARY)
        action_frame.pack(pady=8)
        
        new_game_btn = tk.Button(
            action_frame, text="🔄 New Game", command=self._start_new_game,
            font=self.font_normal, bg=self.COLOR_SUCCESS, fg=self.BG_PRIMARY,
            activebackground="#00ff88", activeforeground=self.BG_PRIMARY,
            padx=20, pady=8, border=0
        )
        new_game_btn.pack()
    
    def _play_sound(self, frequency, duration):
        """Play a beep sound on Windows."""
        try:
            winsound.Beep(frequency, duration)
        except:
            pass
    
    def _shake_window(self):
        """Shake window on wrong guess."""
        for i in range(4):
            self.root.after(i * 50, lambda offset=i * 5: self.root.geometry(f"900x750+{offset if i % 2 == 0 else -offset}+0") if i < 3 else None)
        self.root.after(200, lambda: self.root.geometry("900x750"))
    
    def _jiggle_word(self):
        """Jiggle the word display on wrong guess."""
        original_fg = self.display_label.cget("fg")
        for i in range(4):
            self.root.after(i * 75, lambda: self.display_label.config(fg=self.COLOR_ERROR if i % 2 == 0 else original_fg))
        self.root.after(300, lambda: self.display_label.config(fg=original_fg))
    
    def _celebrate(self):
        """Animate celebration on win."""
        for i in range(3):
            self.display_label.config(fg=self.COLOR_SUCCESS if i % 2 == 0 else "#00ff88")
            self.root.after(i * 200, lambda f=self.display_label: None)
        self.display_label.config(fg=self.COLOR_SUCCESS)
    
    def _get_next_encouragement(self):
        """Get next encouragement message."""
        msg = self.ENCOURAGEMENTS[self.current_encouragement_index]
        self.current_encouragement_index = (self.current_encouragement_index + 1) % len(self.ENCOURAGEMENTS)
        return msg
    
    def _start_new_game(self):
        """Start a new game with selected difficulty."""
        difficulty = self.difficulty_var.get()
        self.game.new_game(difficulty)
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.message_label.config(text="", fg=self.FG_PRIMARY)
        self.encouragement_label.config(text=self._get_next_encouragement(), fg=self.COLOR_SUCCESS)
        self.stats_label.config(text=self.stats.get_summary())
        self.category_label.config(text=f"Hint: {self.game.category}")
        self._update_ui()
    
    def _on_difficulty_change(self):
        """Restart game when difficulty changes."""
        self._start_new_game()
    
    def _on_submit(self):
        """Read entry, process guess, and update UI."""
        if self.game.game_over:
            messagebox.showinfo("Game Over", "Start a new game to play again!")
            return
        
        letter = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        self.entry.focus()
        
        if not letter:
            return
        
        result = self.game.guess(letter)
        
        if result == "invalid":
            self.message_label.config(text="❌ Invalid input! Enter one letter.", fg=self.COLOR_ERROR)
            self._play_sound(400, 200)
        elif result == "already":
            self.message_label.config(
                text=f"⚠️  You already guessed '{letter}'", fg=self.COLOR_WARNING
            )
            self._play_sound(500, 150)
        elif result == "correct":
            self.message_label.config(
                text=f"✨ Correct! '{letter}' is in the word! Keep going!", fg=self.COLOR_SUCCESS
            )
            self._play_sound(800, 100)
        elif result == "wrong":
            self.message_label.config(
                text=f"💥 Oops! '{letter}' is not in the word. Try again!", fg=self.COLOR_ERROR
            )
            self._play_sound(300, 200)
            self._jiggle_word()
            self._break_heart()
        elif result == "win":
            self.message_label.config(
                text=f"🎉 YOU WIN!!! The word is '{self.game.word}' - Amazing work!",
                fg=self.COLOR_SUCCESS
            )
            self._play_sound(1000, 100)
            self._play_sound(1200, 100)
            self._play_sound(1000, 200)
            self._celebrate()
            self.stats.win()
            self.stats_label.config(text=self.stats.get_summary())
        elif result == "lose":
            self.message_label.config(
                text=f"💀 Game Over! The word was '{self.game.word}' - Better luck next time!",
                fg=self.COLOR_ERROR
            )
            self._play_sound(200, 300)
            self._shake_window()
            self.stats.lose()
            self.stats_label.config(text=self.stats.get_summary())
        
        self._update_ui()
    
    def _update_ui(self):
        """Sync all labels to game state."""
        # Display hangman
        self.hangman_label.config(text=self.game.hangman_stage)
        
        # Display word
        if self.game.game_over:
            if self.game.won:
                self.display_label.config(text=self.game.word, fg=self.COLOR_SUCCESS)
            else:
                self.display_label.config(text=self.game.word, fg=self.COLOR_ERROR)
        else:
            self.display_label.config(text=self.game.display_word, fg=self.FG_ACCENT)
        
        # Attempts left
        attempts_left = self.game.attempts_left
        hearts = "❤️ " * attempts_left + "🖤 " * len(self.game.wrong_guesses)
        self.attempts_label.config(
            text=hearts,
            fg=self.COLOR_SUCCESS if attempts_left > 2 else self.COLOR_WARNING if attempts_left > 0 else self.COLOR_ERROR
        )
        
        # Wrong guesses
        self.wrong_label.config(text=self.game.get_wrong_letters())


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
