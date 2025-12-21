"""
Achievement tracker - monitors game events and triggers achievements
"""

class AchievementTracker:
    """Tracks game events and triggers achievements"""
    
    def __init__(self, achievement_manager):
        self.manager = achievement_manager
        
    def check_all(self):
        """Check all conditions based on current stats"""
        stats = self.manager.stats
        
        # Progress & Exploration
        if stats['orbs_destroyed'] >= 50:
            self.manager.unlock('orb_breaker')
        if stats['orbs_destroyed'] >= 250:
            self.manager.unlock('orb_hunter')
        if stats['orbs_destroyed'] >= 1000:
            self.manager.unlock('orb_annihilator')
        
        if stats['levels_completed'] >= 1:
            self.manager.unlock('first_escape')
        if stats['max_level_reached'] >= 10:
            self.manager.unlock('beyond_void')
        if stats['max_level_reached'] >= 25:
            self.manager.unlock('edge_cosmos')
        if stats['max_level_reached'] >= 50:
            self.manager.unlock('dimension_master')
        
        # Skill & Combat
        if stats['consecutive_hits'] >= 10:
            self.manager.unlock('perfect_aim')
        
        if stats['max_combo'] >= 5:
            self.manager.unlock('combo_apprentice')
        if stats['max_combo'] >= 10:
            self.manager.unlock('combo_master')
        
        if stats['danger_time'] >= 5:
            self.manager.unlock('no_panic')
        if stats['danger_time'] >= 10:
            self.manager.unlock('calm_pressure')
        
        # Black Hole & Physics
        if stats['black_hole_enters'] >= 1:
            self.manager.unlock('gravity_victim')
        if stats['black_hole_enters'] >= 10:
            self.manager.unlock('void_stares')
        
        # Lore & Story
        if stats['story_viewed']:
            self.manager.unlock('ancient_awakens')
        if stats['story_completed']:
            self.manager.unlock('temple_echoes')
        
        if stats['story_completed'] and stats['max_level_reached'] >= 25:
            self.manager.unlock('chosen_tiger')
        if stats['story_completed'] and stats['max_level_reached'] >= 50:
            self.manager.unlock('balance_keeper')
        
        # Endurance & Dedication
        if stats['total_playtime'] >= 1800:  # 30 minutes
            self.manager.unlock('endless_traveler')
        if stats['total_playtime'] >= 3600:  # 1 hour
            self.manager.unlock('cosmic_journey')
        
        if stats['continuous_playtime'] >= 900:  # 15 minutes
            self.manager.unlock('no_escape')
        
        if stats['game_overs'] >= 1:
            self.manager.unlock('return_void')
        
        # Secret
        if stats['continuous_playtime'] >= 1800 and stats['game_overs'] == 0:
            self.manager.unlock('ancient_alliance')
        
        if stats['idle_time'] >= 10:
            self.manager.unlock('tiger_watches')
    
    def on_game_start(self):
        """Called when game starts"""
        self.manager.unlock('first_launch')
        self.manager.stats['continuous_playtime'] = 0
    
    def on_orb_destroyed(self, count=1):
        """Called when orbs are destroyed"""
        self.manager.stats['orbs_destroyed'] += count
        self.check_all()
    
    def on_level_complete(self, level):
        """Called when level is completed"""
        self.manager.stats['levels_completed'] += 1
        self.manager.stats['max_level_reached'] = max(
            self.manager.stats['max_level_reached'], 
            level
        )
        self.check_all()
    
    def on_combo(self, combo):
        """Called when combo is achieved"""
        self.manager.stats['max_combo'] = max(
            self.manager.stats['max_combo'],
            combo
        )
        self.check_all()
    
    def on_shot_fired(self, hit):
        """Called when shot is fired"""
        self.manager.stats['shots_fired'] += 1
        
        if hit:
            self.manager.stats['shots_hit'] += 1
            self.manager.stats['consecutive_hits'] += 1
        else:
            self.manager.stats['consecutive_hits'] = 0
        
        self.check_all()
    
    def on_danger_survived(self, duration):
        """Called when surviving in danger state"""
        self.manager.stats['danger_time'] = max(
            self.manager.stats['danger_time'],
            duration
        )
        self.check_all()
    
    def on_black_hole_enter(self):
        """Called when entering black hole"""
        self.manager.unlock('event_horizon')
        self.manager.stats['black_hole_enters'] += 1
        self.check_all()
    
    def on_story_viewed(self, completed=False):
        """Called when story is viewed"""
        self.manager.stats['story_viewed'] = True
        if completed:
            self.manager.stats['story_completed'] = True
        self.check_all()
    
    def on_game_over(self):
        """Called on game over"""
        self.manager.stats['game_overs'] += 1
        self.manager.stats['continuous_playtime'] = 0
        self.check_all()
    
    def update_playtime(self, dt):
        """Update playtime counters"""
        self.manager.stats['total_playtime'] += dt
        self.manager.stats['continuous_playtime'] += dt
        self.check_all()
    
    def update_idle_time(self, dt):
        """Update idle time (main menu)"""
        self.manager.stats['idle_time'] += dt
        self.check_all()
    
    def on_level_complete_close_call(self, orbs_remaining):
        """Called when level completed with few orbs"""
        if orbs_remaining == 1:
            self.manager.unlock('one_shot')
    
    def on_match(self, orb_count):
        """Called when match is made"""
        if orb_count >= 15:
            self.manager.unlock('unstoppable_chain')
    
    def on_portal_entered(self):
        """Called when orb enters portal"""
        self.manager.unlock('into_portal')
    
    def on_black_hole_escape(self):
        """Called when escaping black hole safely"""
        self.manager.unlock('gravity_dancer')
    
    def on_slow_motion_survived(self):
        """Called when surviving slow motion"""
        self.manager.unlock('slow_hero')
    
    def on_level_with_black_hole(self):
        """Called when completing level with black hole active"""
        self.manager.unlock('singularity_escape')