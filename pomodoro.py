import sys
sys.path.insert(0, r'D:\Lib\site-packages')
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                               QFrame, QMessageBox, QGraphicsDropShadowEffect,
                               QProgressBar, QSlider, QSystemTrayIcon, QMenu,
                               QDialog, QScrollArea, QGridLayout, QGraphicsOpacityEffect)
from PySide6.QtCore import QTimer, Qt, QTime, Signal, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QPainter, QFontDatabase, QIcon, QPen, QPainterPath
import math
import random
import json
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


# ============ 1. SUPERCLASS (ABSTRACT BASE CLASS) ============
class TimerMode(ABC):
    """Superclass - Abstract class for all timer modes"""
    def __init__(self, name, duration, color, icon, sound_file=None):
        self._name = name
        self._duration = duration
        self._color = color
        self._icon = icon
        self._sound_file = sound_file
        self._is_active = False
    
    @property
    def name(self):
        return self._name
    
    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        if value > 0 and value <= 120:
            self._duration = value
    
    @property
    def color(self):
        return self._color
    
    @property
    def icon(self):
        return self._icon
    
    @abstractmethod
    def get_message(self):
        pass
    
    @abstractmethod
    def get_style(self):
        pass


# ============ 2. SUBCLASSES ============
class WorkMode(TimerMode):
    def __init__(self):
        super().__init__("Focus Time", 25, "#e94560", "💪")
        self._quote_list = [
            "Focus on being productive instead of busy",
            "The secret of getting ahead is getting started",
            "Work hard in silence, let success make the noise",
        ]
    
    def get_message(self):
        return f"🎉 Great job! You completed a Pomodoro! Time for a break! ☕"
    
    def get_style(self):
        return "color: #ffffff; font-size: 18px; font-weight: bold;"
    
    def get_random_quote(self):
        return random.choice(self._quote_list)


class BreakMode(TimerMode):
    def __init__(self):
        super().__init__("Break Time", 5, "#7CFC00", "☕")
        self._relax_tips = ["Stretch your legs!", "Drink some water!", "Look away from screen!"]
    
    def get_message(self):
        return f"💪 Break's over! Ready to crush your next pomodoro?"
    
    def get_style(self):
        return "color: #7CFC00; font-size: 18px; font-weight: bold;"
    
    def get_random_tip(self):
        return random.choice(self._relax_tips)


class LongBreakMode(TimerMode):
    def __init__(self):
        super().__init__("Long Break", 15, "#FFD700", "🌟")
    
    def get_message(self):
        return f"✨ Amazing! You completed 4 Pomodoros! Take a long break! 🎉"
    
    def get_style(self):
        return "color: #FFD700; font-size: 18px; font-weight: bold;"


# ============ 3. STATISTICS MANAGER CLASS ============
class StatisticsManager:
    def __init__(self, data_file="pomodoro_stats.json"):
        self._data_file = data_file
        self._total_pomodoros = 0
        self._total_focus_time = 0
        self._total_break_time = 0
        self._daily_stats = {}
        self._load_stats()
    
    def _load_stats(self):
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    self._total_pomodoros = data.get('total_pomodoros', 0)
                    self._total_focus_time = data.get('total_focus_time', 0)
                    self._total_break_time = data.get('total_break_time', 0)
                    self._daily_stats = data.get('daily_stats', {})
            except:
                pass
    
    def _save_stats(self):
        data = {
            'total_pomodoros': self._total_pomodoros,
            'total_focus_time': self._total_focus_time,
            'total_break_time': self._total_break_time,
            'daily_stats': self._daily_stats
        }
        with open(self._data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_pomodoro(self, focus_minutes):
        self._total_pomodoros += 1
        self._total_focus_time += focus_minutes
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self._daily_stats:
            self._daily_stats[today] = {'pomodoros': 0, 'focus_minutes': 0}
        self._daily_stats[today]['pomodoros'] += 1
        self._daily_stats[today]['focus_minutes'] += focus_minutes
        self._save_stats()
    
    def add_break(self, break_minutes):
        self._total_break_time += break_minutes
        self._save_stats()
    
    @property
    def total_pomodoros(self):
        return self._total_pomodoros
    
    @property
    def total_focus_hours(self):
        return round(self._total_focus_time / 60, 1)
    
    @property
    def total_focus_time(self):
        return self._total_focus_time
    
    @property
    def total_break_time(self):
        return self._total_break_time
    
    @property
    def today_pomodoros(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self._daily_stats.get(today, {}).get('pomodoros', 0)
    
    def get_last_7_days(self):
        result = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_name = (datetime.now() - timedelta(days=i)).strftime("%a")
            count = self._daily_stats.get(date, {}).get('pomodoros', 0)
            minutes = self._daily_stats.get(date, {}).get('focus_minutes', 0)
            result.append({'date': day_name, 'full_date': date, 'count': count, 'minutes': minutes})
        return result
    
    def get_monthly_stats(self):
        monthly = {}
        for date_str, stats in self._daily_stats.items():
            month = date_str[:7]
            if month not in monthly:
                monthly[month] = {'pomodoros': 0, 'minutes': 0}
            monthly[month]['pomodoros'] += stats['pomodoros']
            monthly[month]['minutes'] += stats['focus_minutes']
        return monthly


# ============ 4. CUSTOM WIDGETS FOR STATISTICS ============
class GlassCard(QFrame):
    """Glass morphism card with shadow and hover effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            GlassCard {
                background: rgba(30, 30, 50, 0.6);
                border: 1px solid rgba(233, 69, 96, 0.3);
                border-radius: 20px;
            }
            GlassCard:hover {
                background: rgba(40, 40, 60, 0.8);
                border: 1px solid rgba(233, 69, 96, 0.6);
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)


class AnimatedProgressBar(QProgressBar):
    """Progress bar with animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setValue(self, value):
        self.animation.stop()
        self.animation.setEndValue(value)
        self.animation.start()


class StatsNumberLabel(QLabel):
    """Label with counting animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_value = 0
        self.target_value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.valueChanged.connect(self._update_number)
    
    def get_value(self):
        return self.current_value
    
    def set_value(self, value):
        self.target_value = int(value)
        self.animation.setEndValue(self.target_value)
        self.animation.start()
    
    def _update_number(self, val):
        self.current_value = int(val)
        self.setText(str(self.current_value))
    
    value = property(get_value, set_value)


# ============ 5. STATISTICS DIALOG (PREMIUM VERSION) ============
class StatisticsDialog(QDialog):
    def __init__(self, stats_manager, parent=None):
        super().__init__(parent)
        self.stats = stats_manager
        self.setWindowTitle("✨ Analytics Dashboard ✨")
        self.setMinimumSize(700, 650)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Main container
        container = GlassCard()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header with close button
        header_layout = QHBoxLayout()
        
        title_wrapper = QWidget()
        title_layout = QHBoxLayout(title_wrapper)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_icon = QLabel("✨")
        title_icon.setFont(QFont("Segoe UI Emoji", 28))
        title_layout.addWidget(title_icon)
        
        title = QLabel("STATISTICS DASHBOARD")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e94560; letter-spacing: 2px;")
        title_layout.addWidget(title)
        
        header_layout.addWidget(title_wrapper)
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(233, 69, 96, 0.2);
                border: 2px solid #e94560;
                border-radius: 17px;
                font-size: 18px;
                font-weight: bold;
                color: #e94560;
            }
            QPushButton:hover {
                background: #e94560;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)
        
        container_layout.addLayout(header_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(30, 30, 50, 0.5);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #e94560;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff6b6b;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(25)
        
        # ===== STATS CARDS ROW =====
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Card 1: Total Pomodoros
        card1 = self._create_stats_card("🍅", "TOTAL POMODOROS", self.stats.total_pomodoros, "#e94560")
        cards_layout.addWidget(card1)
        
        # Card 2: Focus Hours
        card2 = self._create_stats_card("⏱️", "FOCUS TIME", f"{self.stats.total_focus_hours}", "#7CFC00", "hours")
        cards_layout.addWidget(card2)
        
        # Card 3: Daily Average
        avg_per_day = round(self.stats.total_pomodoros / max(1, len(self.stats._daily_stats)), 1)
        card3 = self._create_stats_card("📊", "DAILY AVG", avg_per_day, "#FFD700", "🍅/day")
        cards_layout.addWidget(card3)
        
        # Card 4: Streak
        streak = self._get_current_streak()
        card4 = self._create_stats_card("🔥", "CURRENT STREAK", streak, "#ff6b6b", "days")
        cards_layout.addWidget(card4)
        
        scroll_layout.addLayout(cards_layout)
        
        # ===== WEEKLY CHART SECTION =====
        chart_section = GlassCard()
        chart_section.setStyleSheet("GlassCard { background: rgba(20, 20, 40, 0.8); }")
        chart_layout = QVBoxLayout(chart_section)
        
        chart_header = QHBoxLayout()
        chart_title = QLabel("📈 WEEKLY PROGRESS")
        chart_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #e94560;")
        chart_header.addWidget(chart_title)
        
        total_week = sum(d['count'] for d in self.stats.get_last_7_days())
        week_badge = QLabel(f"🔥 {total_week} this week")
        week_badge.setStyleSheet("""
            background: rgba(233, 69, 96, 0.2);
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: bold;
        """)
        chart_header.addWidget(week_badge)
        chart_header.addStretch()
        chart_layout.addLayout(chart_header)
        
        # Animated bar chart
        weekly_data = self.stats.get_last_7_days()
        max_count = max([d['count'] for d in weekly_data]) if weekly_data else 1
        
        for day_data in weekly_data:
            bar_widget = QWidget()
            bar_layout = QHBoxLayout(bar_widget)
            bar_layout.setContentsMargins(5, 5, 5, 5)
            
            day_label = QLabel(day_data['date'])
            day_label.setFixedWidth(50)
            day_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            day_label.setStyleSheet("color: #ffffff;")
            
            bar_container = QWidget()
            bar_container.setStyleSheet("""
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            """)
            bar_container_layout = QVBoxLayout(bar_container)
            bar_container_layout.setContentsMargins(0, 0, 0, 0)
            
            bar = AnimatedProgressBar()
            bar.setRange(0, max(1, max_count))
            bar.setValue(day_data['count'])
            bar.setFormat(f"{day_data['count']} 🍅")
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 10px;
                    background: transparent;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    height: 40px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #e94560, stop:1 #ff6b6b);
                    border-radius: 10px;
                }}
            """)
            
            bar_container_layout.addWidget(bar)
            bar_layout.addWidget(day_label)
            bar_layout.addWidget(bar_container)
            scroll_layout.addWidget(bar_widget)
        
        chart_layout.addStretch()
        scroll_layout.addWidget(chart_section)
        
        # ===== PIE CHART SECTION (Custom drawn) =====
        pie_section = GlassCard()
        pie_section.setStyleSheet("GlassCard { background: rgba(20, 20, 40, 0.8); }")
        pie_layout = QVBoxLayout(pie_section)
        
        pie_title = QLabel("🥧 TIME DISTRIBUTION")
        pie_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        pie_title.setStyleSheet("color: #e94560;")
        pie_layout.addWidget(pie_title)
        
        pie_chart_widget = PieChartWidget(self.stats.total_focus_time, self.stats.total_break_time)
        pie_chart_widget.setMinimumHeight(250)
        pie_layout.addWidget(pie_chart_widget)
        
        scroll_layout.addWidget(pie_section)
        
        # ===== ACHIEVEMENTS SECTION =====
        achievements_section = GlassCard()
        achievements_section.setStyleSheet("GlassCard { background: rgba(20, 20, 40, 0.8); }")
        achievements_layout = QVBoxLayout(achievements_section)
        
        ach_title = QLabel("🏆 ACHIEVEMENTS UNLOCKED 🏆")
        ach_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        ach_title.setStyleSheet("color: #FFD700;")
        achievements_layout.addWidget(ach_title)
        
        achievements_grid = QGridLayout()
        achievements_grid.setSpacing(10)
        
        achievements = self._get_achievements()
        for i, ach in enumerate(achievements):
            ach_widget = self._create_achievement_badge(ach['icon'], ach['title'], ach['unlocked'])
            achievements_grid.addWidget(ach_widget, i // 2, i % 2)
        
        achievements_layout.addLayout(achievements_grid)
        scroll_layout.addWidget(achievements_section)
        
        # ===== MOTIVATIONAL QUOTE =====
        quote_widget = GlassCard()
        quote_layout = QVBoxLayout(quote_widget)
        
        quote_text = QLabel(self._get_motivational_quote())
        quote_text.setWordWrap(True)
        quote_text.setAlignment(Qt.AlignCenter)
        quote_text.setStyleSheet("""
            color: #cccccc;
            font-size: 13px;
            font-style: italic;
            padding: 15px;
        """)
        quote_layout.addWidget(quote_text)
        
        scroll_layout.addWidget(quote_widget)
        
        scroll.setWidget(scroll_widget)
        container_layout.addWidget(scroll)
        
        main_layout.addWidget(container)
    
    def _create_stats_card(self, icon, title, value, color, suffix=""):
        card = GlassCard()
        card.setFixedHeight(120)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #aaaaaa; letter-spacing: 1px;")
        
        if isinstance(value, (int, float)):
            value_label = StatsNumberLabel()
            value_label.value = value
            display_text = f"{value}{suffix}"
        else:
            value_label = QLabel()
            display_text = f"{value}{suffix}"
        
        value_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        value_label.setText(display_text)
        
        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        return card
    
    def _create_achievement_badge(self, icon, title, unlocked):
        widget = QFrame()
        if unlocked:
            widget.setStyleSheet("""
                QFrame {
                    background: rgba(255, 215, 0, 0.15);
                    border: 1px solid #FFD700;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        else:
            widget.setStyleSheet("""
                QFrame {
                    background: rgba(100, 100, 100, 0.1);
                    border: 1px solid #444444;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        if unlocked:
            title_label.setStyleSheet("color: #FFD700;")
        else:
            title_label.setStyleSheet("color: #666666;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        if unlocked:
            check_label = QLabel("✓")
            check_label.setStyleSheet("color: #7CFC00; font-size: 16px; font-weight: bold;")
            layout.addWidget(check_label)
        
        return widget
    
    def _get_achievements(self):
        total = self.stats.total_pomodoros
        achievements = []
        
        achievements.append({
            'icon': '🍅',
            'title': 'First Pomodoro',
            'unlocked': total >= 1
        })
        achievements.append({
            'icon': '🌟',
            'title': 'Rookie (5 Pomodoros)',
            'unlocked': total >= 5
        })
        achievements.append({
            'icon': '🎯',
            'title': 'Consistent (10 Pomodoros)',
            'unlocked': total >= 10
        })
        achievements.append({
            'icon': '💪',
            'title': 'Warrior (20 Pomodoros)',
            'unlocked': total >= 20
        })
        achievements.append({
            'icon': '🏆',
            'title': 'Elite (50 Pomodoros)',
            'unlocked': total >= 50
        })
        achievements.append({
            'icon': '👑',
            'title': 'Legend (100+ Pomodoros)',
            'unlocked': total >= 100
        })
        achievements.append({
            'icon': '🔥',
            'title': '3-Day Streak',
            'unlocked': self._get_current_streak() >= 3
        })
        achievements.append({
            'icon': '⚡',
            'title': '7-Day Streak',
            'unlocked': self._get_current_streak() >= 7
        })
        
        return achievements
    
    def _get_current_streak(self):
        streak = 0
        for i in range(30):
            check_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if self.stats._daily_stats.get(check_date, {}).get('pomodoros', 0) > 0:
                streak += 1
            else:
                break
        return streak
    
    def _get_motivational_quote(self):
        quotes = [
            "🚀 " + '"The secret of getting ahead is getting started." - Mark Twain',
            "💪 " + '"Small daily improvements are the key to staggering long-term results."',
            "🎯 " + '"The future depends on what you do today." - Mahatma Gandhi',
            "🌟 " + '"You don\'t have to be great to start, but you have to start to be great."',
            "🔥 " + '"Your only limit is your mind. Keep pushing forward!"'
        ]
        return random.choice(quotes)
    
    def _setup_animations(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


class PieChartWidget(QWidget):
    """Custom pie chart widget"""
    def __init__(self, focus_time, break_time, parent=None):
        super().__init__(parent)
        self.focus_time = focus_time
        self.break_time = break_time
        self.setMinimumHeight(200)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = self.focus_time + self.break_time
        if total == 0:
            # Draw empty state
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(60, 60, 60))
            painter.drawEllipse(50, 25, 150, 150)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "Complete sessions\nto see chart")
            return
        
        # Calculate angles (in 16ths of a degree)
        focus_angle = int((self.focus_time / total) * 360 * 16)
        break_angle = 360 * 16 - focus_angle
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 3
        
        # Draw pie slices
        painter.setPen(Qt.NoPen)
        
        # Focus slice
        gradient1 = QLinearGradient(center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        gradient1.setColorAt(0, QColor(233, 69, 96))
        gradient1.setColorAt(1, QColor(255, 107, 107))
        painter.setBrush(gradient1)
        painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2, 90 * 16, -focus_angle)
        
        # Break slice
        gradient2 = QLinearGradient(center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        gradient2.setColorAt(0, QColor(124, 252, 0))
        gradient2.setColorAt(1, QColor(144, 238, 144))
        painter.setBrush(gradient2)
        painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2, (90 * 16 - focus_angle), -break_angle)
        
        # Draw center circle (donut hole effect)
        painter.setBrush(QColor(26, 26, 46))
        painter.drawEllipse(center_x - radius//2, center_y - radius//2, radius, radius)
        
        # Draw labels
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        focus_percent = round((self.focus_time / total) * 100, 1)
        break_percent = round((self.break_time / total) * 100, 1)
        
        painter.drawText(center_x - 40, center_y - 30, f"Focus")
        painter.drawText(center_x - 40, center_y - 15, f"{focus_percent}%")
        painter.setPen(QPen(QColor(124, 252, 0), 2))
        painter.drawText(center_x - 40, center_y + 10, f"Break")
        painter.drawText(center_x - 40, center_y + 25, f"{break_percent}%")


# ============ 6. CIRCULAR PROGRESS WIDGET ============
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 100
        self._color = QColor(233, 69, 96)
        self.setMinimumSize(200, 200)
    
    def setProgress(self, value):
        self._progress = value
        self.update()
    
    def setColor(self, color):
        self._color = color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 10
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(60, 60, 60))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        angle = (self._progress / 100) * 360 * 16
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, self._color)
        gradient.setColorAt(1, self._color.darker(120))
        
        painter.setBrush(Qt.NoBrush)
        pen = painter.pen()
        pen.setWidth(15)
        pen.setBrush(gradient)
        painter.setPen(pen)
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 90 * 16, -angle)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(43, 43, 43))
        painter.drawEllipse(center_x - radius + 20, center_y - radius + 20, 
                          (radius - 20) * 2, (radius - 20) * 2)


# ============ 7. MAIN APPLICATION ============
class PomodoroTimer(QMainWindow):
    mode_changed = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🍅 Pomodoro Focus Timer")
        self.setFixedSize(500, 750)
        
        self._is_running = False
        self._time_left = 25 * 60
        self._pomodoro_count = 0
        
        self.modes = [WorkMode(), BreakMode(), LongBreakMode()]
        self._current_mode = self.modes[0]
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_timer)
        
        self._stats = StatisticsManager()
        
        self._setup_ui()
        self._set_style()
        
        self.mode_changed.connect(self._on_mode_changed)
        self._on_mode_changed(self._current_mode)
    
    @property
    def current_mode(self):
        return self._current_mode
    
    @current_mode.setter
    def current_mode(self, mode):
        if mode in self.modes:
            self._current_mode = mode
            self._time_left = mode.duration * 60
            self.mode_changed.emit(mode)
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        header_layout = QHBoxLayout()
        
        self.stats_btn = QPushButton("📊 STATS")
        self.stats_btn.setFixedSize(100, 40)
        self.stats_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #e94560, stop:1 #ff6b6b);
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.stats_btn.clicked.connect(self._show_statistics)
        header_layout.addWidget(self.stats_btn)
        
        header_layout.addStretch()
        
        self.pomodoro_counter = QLabel(f"🍅 {self._stats.total_pomodoros}")
        self.pomodoro_counter.setStyleSheet("background: rgba(233, 69, 96, 0.2); padding: 5px 15px; border-radius: 20px;")
        header_layout.addWidget(self.pomodoro_counter)
        
        self.daily_counter = QLabel(f"📅 {self._stats.today_pomodoros}")
        self.daily_counter.setStyleSheet("background: rgba(124, 252, 0, 0.2); padding: 5px 15px; border-radius: 20px;")
        header_layout.addWidget(self.daily_counter)
        
        main_layout.addLayout(header_layout)
        
        self.circular_progress = CircularProgress()
        main_layout.addWidget(self.circular_progress, alignment=Qt.AlignCenter)
        
        self.timer_display = QLabel()
        self.timer_display.setAlignment(Qt.AlignCenter)
        self.timer_display.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        main_layout.addWidget(self.timer_display, alignment=Qt.AlignCenter)
        
        self.mode_label = QLabel()
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(self.mode_label)
        
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        main_layout.addWidget(self.message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_btn = QPushButton("▶ START")
        self.pause_btn = QPushButton("⏸ PAUSE")
        self.reset_btn = QPushButton("⟳ RESET")
        self.skip_btn = QPushButton("⏩ SKIP")
        
        for btn in [self.start_btn, self.pause_btn, self.reset_btn, self.skip_btn]:
            btn.setMinimumHeight(45)
            btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        self.pause_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.skip_btn)
        
        main_layout.addLayout(button_layout)
        
        self.start_btn.clicked.connect(self._start_timer)
        self.pause_btn.clicked.connect(self._pause_timer)
        self.reset_btn.clicked.connect(self._reset_timer)
        self.skip_btn.clicked.connect(self._skip_mode)
    
    def _set_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0f0f1a, stop:0.5 #1a1a2e, stop:1 #16213e);
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e94560, stop:1 #c73b54);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff6b6b, stop:1 #e94560); }
            QPushButton:pressed { background: #c73b54; }
            QPushButton:disabled { background: #4a4a4a; color: #888888; }
        """)
    
    def _update_message(self):
        if isinstance(self._current_mode, WorkMode):
            self.message_label.setText(f'💪 "{self._current_mode.get_random_quote()}"')
        elif isinstance(self._current_mode, BreakMode):
            self.message_label.setText(f'☕ {self._current_mode.get_random_tip()}')
        else:
            self.message_label.setText("🌟 Take a well-deserved long break!")
    
    def _on_mode_changed(self, mode):
        self.mode_label.setText(f"{mode.icon} {mode.name} {mode.icon}")
        self.mode_label.setStyleSheet(mode.get_style())
        self.circular_progress.setColor(QColor(mode.color))
        self._update_message()
        self._update_display()
    
    def _update_display(self):
        minutes = self._time_left // 60
        seconds = self._time_left % 60
        self.timer_display.setText(f"{minutes:02d}:{seconds:02d}")
        total_time = self._current_mode.duration * 60
        progress = (self._time_left / total_time) * 100 if total_time > 0 else 0
        self.circular_progress.setProgress(progress)
    
    def _update_timer(self):
        if self._time_left > 0:
            self._time_left -= 1
            self._update_display()
        else:
            self._timer.stop()
            self._is_running = False
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.start_btn.setText("▶ START")
            
            if isinstance(self._current_mode, WorkMode):
                self._stats.add_pomodoro(self._current_mode.duration)
                self.pomodoro_counter.setText(f"🍅 {self._stats.total_pomodoros}")
                self.daily_counter.setText(f"📅 {self._stats.today_pomodoros}")
                self._pomodoro_count += 1
            elif isinstance(self._current_mode, BreakMode) or isinstance(self._current_mode, LongBreakMode):
                self._stats.add_break(self._current_mode.duration)
            
            msg = QMessageBox(self)
            msg.setWindowTitle("🎉 Timer Complete!")
            msg.setText(self._current_mode.get_message())
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            if isinstance(self._current_mode, WorkMode):
                if self._pomodoro_count % 4 == 0:
                    self.current_mode = self.modes[2]
                else:
                    self.current_mode = self.modes[1]
            else:
                self.current_mode = self.modes[0]
            
            self._update_display()
    
    def _start_timer(self):
        if not self._is_running:
            self._timer.start(1000)
            self._is_running = True
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.start_btn.setText("▶ RUNNING")
    
    def _pause_timer(self):
        if self._is_running:
            self._timer.stop()
            self._is_running = False
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.start_btn.setText("▶ RESUME")
    
    def _reset_timer(self):
        self._timer.stop()
        self._is_running = False
        self.current_mode = self.modes[0]
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.start_btn.setText("▶ START")
    
    def _skip_mode(self):
        self._timer.stop()
        self._is_running = False
        
        if isinstance(self._current_mode, WorkMode):
            if self._pomodoro_count % 4 == 3:
                self.current_mode = self.modes[2]
            else:
                self.current_mode = self.modes[1]
        else:
            self.current_mode = self.modes[0]
        
        self._update_display()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.start_btn.setText("▶ START")
    
    def _show_statistics(self):
        dialog = StatisticsDialog(self._stats, self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec())