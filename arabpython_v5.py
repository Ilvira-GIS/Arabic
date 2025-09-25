import pygame
import sys
import random
import os
import json

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арабский Глагольный Квиз")

# Colors
BACKGROUND = (240, 240, 230)
TEXT_COLOR = (40, 40, 40)
ARABIC_COLOR = (50, 80, 120)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
CORRECT_COLOR = (50, 150, 50)
HIGHLIGHT_COLOR = (220, 220, 150)
TENSE_SELECT_COLOR = (180, 200, 220)
VERB_SELECT_COLOR = (200, 220, 180)
EXIT_BUTTON_COLOR = (180, 70, 70)
EXIT_BUTTON_HOVER = (210, 90, 90)
SCROLLBAR_COLOR = (150, 150, 150)
SCROLLBAR_HOVER = (120, 120, 120)

# Load Arabic font from file
def load_arabic_font():
    font_paths = [
        os.path.join(os.path.dirname(__file__), "NotoSansArabic.ttf"),
        os.path.join(os.path.dirname(sys.executable), "NotoSansArabic.ttf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "NotoSansArabic.ttf"),
        "NotoSansArabic.ttf"  # Try current directory
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                arabic_font = pygame.font.Font(font_path, 32)
                arabic_font.set_script("Arab")
                arabic_font.set_direction(pygame.DIRECTION_RTL)
                print(f"Successfully loaded font from: {font_path}")
                return arabic_font
        except Exception as e:
            print(f"Error loading font from {font_path}: {e}")
            continue
    
    print("Custom Arabic font not found. Falling back to system font.")
    return pygame.font.SysFont("Arial", 32)

# Load the font
arabic_font = load_arabic_font()

# Other fonts
title_font = pygame.font.SysFont("Arial", 40, bold=True)
question_font = pygame.font.SysFont("Arial", 32)
answer_font = pygame.font.SysFont("Arial", 28)
button_font = pygame.font.SysFont("Arial", 24)
meaning_font = pygame.font.SysFont("Arial", 26)
tense_font = pygame.font.SysFont("Arial", 36, bold=True)
verb_font = pygame.font.SysFont("Arial", 30)

# Load verbs from JSON file
def load_verbs():
    try:
        with open('verbs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["verbs"]
    except FileNotFoundError:
        print("verbs.json file not found. Using fallback data.")
        # Fallback data if JSON file is missing
        return [
            {
                "infinitive": "كَتَبَ",
                "meaning": "писать",
                "root": "ك-ت-ب",
                "past": [{"pronoun": "أنا", "conjugation": "كَتَبْتُ", "meaning": "я"}, 
                         {"pronoun": "انتَ", "conjugation": "كَتَبْتَ", "meaning": "ты (м.р.)"}],
                "present": [{"pronoun": "أنا", "conjugation": "أَكْتُبُ", "meaning": "я"}, 
                            {"pronoun": "انتَ", "conjugation": "تَكْتُبُ", "meaning": "ты (м.р.)"}]
            }
        ]

verbs_db = load_verbs()

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=8)
        
        text_surf = button_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class TenseButton:
    def __init__(self, x, y, width, height, text, tense):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.tense = tense
        self.hovered = False
        self.selected = False
        
    def draw(self, surface):
        if self.selected:
            color = BUTTON_COLOR
        else:
            color = BUTTON_HOVER if self.hovered else TENSE_SELECT_COLOR
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=8)
        
        text_surf = tense_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class VerbButton:
    def __init__(self, x, y, width, height, verb_index, text, meaning, is_hard_mode=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.verb_index = verb_index
        self.text = text
        self.meaning = meaning
        self.hovered = False
        self.selected = False
        self.is_hard_mode = is_hard_mode
        
    def draw(self, surface):
        if self.selected:
            color = BUTTON_COLOR
        else:
            color = BUTTON_HOVER if self.hovered else VERB_SELECT_COLOR
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=8)
        
        # For hard mode button, use regular font instead of Arabic font
        if self.is_hard_mode:
            # Draw Russian text for hard mode
            text_surf = verb_font.render(self.text, True, ARABIC_COLOR)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
            surface.blit(text_surf, text_rect)
        else:
            # Draw Arabic text for regular verb buttons
            text_surf = arabic_font.render(self.text, True, ARABIC_COLOR)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
            surface.blit(text_surf, text_rect)
        
        # Draw meaning
        meaning_surf = verb_font.render(self.meaning, True, TEXT_COLOR)
        meaning_rect = meaning_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 15))
        surface.blit(meaning_surf, meaning_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class ScrollBar:
    def __init__(self, x, y, width, height, content_height, visible_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = content_height
        self.visible_height = visible_height
        self.scroll_position = 0
        self.dragging = False
        self.hovered = False
        
        # Calculate scrollbar handle size and position
        self.update_handle()
        
    def update_handle(self):
        # Calculate handle size based on visible area
        handle_height = max(30, (self.visible_height / self.content_height) * self.rect.height)
        self.handle_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + (self.scroll_position / self.content_height) * self.rect.height,
            self.rect.width,
            handle_height
        )
        
    def draw(self, surface):
        # Draw scrollbar background
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=5)
        
        # Draw scrollbar handle
        handle_color = SCROLLBAR_HOVER if self.hovered or self.dragging else SCROLLBAR_COLOR
        pygame.draw.rect(surface, handle_color, self.handle_rect, border_radius=5)
        
    def check_hover(self, pos):
        self.hovered = self.handle_rect.collidepoint(pos)
        return self.hovered
        
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.drag_start_y = mouse_pos[1] - self.handle_rect.y
            elif self.rect.collidepoint(mouse_pos):
                # Click on scrollbar but not on handle - jump to position
                relative_y = mouse_pos[1] - self.rect.y
                self.scroll_position = (relative_y / self.rect.height) * self.content_height
                self.update_handle()
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Drag the scrollbar handle
            new_y = mouse_pos[1] - self.drag_start_y
            new_y = max(self.rect.y, min(new_y, self.rect.y + self.rect.height - self.handle_rect.height))
            
            # Calculate new scroll position
            relative_y = new_y - self.rect.y
            self.scroll_position = (relative_y / (self.rect.height - self.handle_rect.height)) * (self.content_height - self.visible_height)
            self.update_handle()
            
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll with mouse wheel
            self.scroll_position -= event.y * 30  # Scroll speed
            self.scroll_position = max(0, min(self.scroll_position, self.content_height - self.visible_height))
            self.update_handle()
            
        return self.scroll_position

def draw_text_with_background(surface, text, font, color, x, y, bg_color=None):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    
    if bg_color:
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=5)
        pygame.draw.rect(surface, (180, 180, 180), bg_rect, 2, border_radius=5)
    
    surface.blit(text_surface, text_rect)
    return text_rect

def tense_selection_screen():
    clock = pygame.time.Clock()
    
    past_button = TenseButton(WIDTH//2 - 150, HEIGHT//2 - 50, 350, 80, "Прошедшее время", "past")
    present_button = TenseButton(WIDTH//2 - 150, HEIGHT//2 + 50, 350, 80, "Настоящее время", "present")
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if past_button.is_clicked(mouse_pos, event):
                return "past"
            if present_button.is_clicked(mouse_pos, event):
                return "present"
        
        # Update button hover states
        past_button.check_hover(mouse_pos)
        present_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw title
        title_text = title_font.render("Выберите время глагола", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        # Draw tense buttons
        past_button.draw(screen)
        present_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def verb_selection_screen(selected_tense):
    clock = pygame.time.Clock()
    
    # Create scrollable area dimensions
    scroll_area_x = 100
    scroll_area_y = 140
    scroll_area_width = WIDTH - 200
    scroll_area_height = HEIGHT - 250
    scroll_content_height = max(scroll_area_height, (len(verbs_db) // 2 + 2) * 110)  # +2 for hard mode and spacing
    
    # Create scrollbar
    scrollbar = ScrollBar(
        WIDTH - 80, scroll_area_y, 20, scroll_area_height,
        scroll_content_height, scroll_area_height
    )
    
    # Create hard mode button (first button)
    hard_mode_button = VerbButton(
        scroll_area_x + 25, 
        scroll_area_y + 10 - scrollbar.scroll_position, 
        330, 80, -1, "Сложный режим", "Все глаголы перемешаны", is_hard_mode=True
    )
    
    # Create verb buttons
    verb_buttons = []
    for i, verb in enumerate(verbs_db):
        row = i // 2
        col = i % 2
        x = scroll_area_x + 25 + col * 350
        y = scroll_area_y + 120 + row * 110 - scrollbar.scroll_position  # Start below hard mode button
        verb_buttons.append(VerbButton(x, y, 300, 80, i, verb["infinitive"], verb["meaning"]))
    
    # Create exit button (fixed position at bottom)
    exit_button = Button(WIDTH//2 - 150, HEIGHT - 80, 300, 60, "Выход в меню", EXIT_BUTTON_COLOR, EXIT_BUTTON_HOVER)
    
    running = True
    selected_verb_index = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle scrollbar events
            scroll_position = scrollbar.handle_event(event, mouse_pos)
            
            # Update button positions based on scroll
            hard_mode_button.rect.y = scroll_area_y + 10 - scroll_position
            
            for i, button in enumerate(verb_buttons):
                row = i // 2
                button.rect.y = scroll_area_y + 120 + row * 110 - scroll_position
            
            # Check button clicks only if they're visible
            if hard_mode_button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
                if hard_mode_button.is_clicked(mouse_pos, event):
                    selected_verb_index = -1
                    running = False
                    
            for button in verb_buttons:
                if button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
                    if button.is_clicked(mouse_pos, event):
                        selected_verb_index = button.verb_index
                        running = False
                
            if exit_button.is_clicked(mouse_pos, event):
                return "exit"
        
        # Update button hover states for visible buttons only
        scrollbar.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        
        if hard_mode_button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
            hard_mode_button.check_hover(mouse_pos)
            
        for button in verb_buttons:
            if button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
                button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw title
        tense_name = "прошедшем" if selected_tense == "past" else "настоящем"
        title_text = title_font.render(f"Выберите глагол для практики", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        # Create a surface for the scrollable area (optional - for visual clarity)
        # pygame.draw.rect(screen, (250, 250, 250), (scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height), border_radius=10)
        
        # Draw buttons that are within the visible area
        if hard_mode_button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
            hard_mode_button.draw(screen)
            
        for button in verb_buttons:
            if button.rect.colliderect(pygame.Rect(scroll_area_x, scroll_area_y, scroll_area_width, scroll_area_height)):
                button.draw(screen)
        
        # Draw scrollbar
        scrollbar.draw(screen)
        
        # Draw exit button (always visible)
        exit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    return selected_verb_index

def practice_screen(selected_tense, selected_verb_index):
    # Prepare the verb list based on selection
    if selected_verb_index == -1:  # Hard mode - all verbs
        practice_verbs = verbs_db
    else:  # Single verb selected
        practice_verbs = [verbs_db[selected_verb_index]]
    
    # Get the tense name for display
    tense_name = "прошедшем" if selected_tense == "past" else "настоящем"
    
    clock = pygame.time.Clock()
    action_button = Button(WIDTH//2 - 150, HEIGHT - 80, 300, 60, "Показать ответ")
    exit_button = Button(WIDTH//2 - 150, HEIGHT - 150, 300, 60, "Выход в меню", EXIT_BUTTON_COLOR, EXIT_BUTTON_HOVER)
    
    # Initialize quiz with a random verb and pronoun
    current_verb = random.choice(practice_verbs)
    current_pronoun = random.choice(current_verb[selected_tense])
    show_answer = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if action_button.is_clicked(mouse_pos, event):
                if show_answer:
                    # If answer is showing, go to next question
                    current_verb = random.choice(practice_verbs)
                    current_pronoun = random.choice(current_verb[selected_tense])
                    show_answer = False
                    action_button.text = "Показать ответ"
                else:
                    # If answer is not showing, show it
                    show_answer = True
                    action_button.text = "Следующий вопрос"
                    
            if exit_button.is_clicked(mouse_pos, event):
                return True  # Return to main menu
        
        # Update button hover state
        action_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BACKGROUND)
        
        # Draw title
        title_text = title_font.render(f"Арабский квиз", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        # Draw current verb info (only in hard mode) 
        if selected_verb_index == -1:
            # Create the verb info text components
            verb_part1 = "Глагол: "
            verb_infinitive = current_verb['infinitive']
            verb_part2 = f"({current_verb['meaning']})"
            
            # Render each part with the appropriate font
            part1_surface = meaning_font.render(verb_part1, True, (100, 100, 100))
            infinitive_surface = arabic_font.render(verb_infinitive, True, ARABIC_COLOR)
            part2_surface = meaning_font.render(verb_part2, True, (100, 100, 100))
            
            # Calculate total width and starting position
            total_width = part1_surface.get_width() + infinitive_surface.get_width() + part2_surface.get_width() + 10
            start_x = (WIDTH - total_width) // 2
            
            # Draw all parts at the correct y-position 
            screen.blit(part1_surface, (start_x, 110)) 
            screen.blit(infinitive_surface, (start_x + part1_surface.get_width() + 5, 90)) 
            screen.blit(part2_surface, (start_x + part1_surface.get_width() + infinitive_surface.get_width() + 10, 110)) 
        
        # Draw question
        question_text = question_font.render(f"Какой будет форма в {tense_name} времени для:", True, TEXT_COLOR)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 165)) 
        
        # Draw pronoun with background 
        pronoun_rect = draw_text_with_background(
            screen, current_pronoun['pronoun'], arabic_font, 
            ARABIC_COLOR, WIDTH//2, 250, HIGHLIGHT_COLOR
        )
        
        # Draw meaning of the pronoun 
        pronoun_meaning = current_pronoun.get('meaning', '')
        if pronoun_meaning:
            meaning_text = meaning_font.render(pronoun_meaning, True, (80, 80, 80))
            screen.blit(meaning_text, (WIDTH//2 - meaning_text.get_width()//2, 310)) 
        
        # Draw answer if shown 
        if show_answer:
            # Draw answer label aligned with the answer window
            answer_label = answer_font.render("Ответ:", True, TEXT_COLOR)
            screen.blit(answer_label, (WIDTH//2 - 180, 355))
            
            # Draw Arabic conjugation with background
            conjugation_rect = draw_text_with_background(
                screen, current_pronoun['conjugation'], arabic_font, 
                ARABIC_COLOR, WIDTH//2, 365, HIGHLIGHT_COLOR  
            )
        
        # Draw buttons
        action_button.draw(screen)
        exit_button.draw(screen)
        
        # Draw instructions
        instructions = answer_font.render("Подумайте над ответом, затем нажмите кнопку для проверки", True, (100, 100, 100))
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 200))
        
        pygame.display.flip()
        clock.tick(60)
    
    return False  # Return whether to continue running

def main():
    running = True
    while running:
        # Step 1: Tense selection
        selected_tense = tense_selection_screen()
        
        # Step 2: Verb selection
        selected_verb_index = verb_selection_screen(selected_tense)
        
        if selected_verb_index == "exit":  # User clicked exit button
            continue  # Go back to tense selection
        
        # Step 3: Practice
        running = practice_screen(selected_tense, selected_verb_index)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()