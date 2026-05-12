import sys
sys.path.insert(0, r'D:\Lib\site-packages')
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QSpinBox,
                               QFrame, QMessageBox, QGraphicsDropShadowEffect,
                               QProgressBar, QSlider, QSystemTrayIcon, QMenu,
                               QDialog, QScrollArea, QGridLayout, QGraphicsOpacityEffect,
                               QSizePolicy, QSpacerItem)
from PySide6.QtCore import QTimer, Qt, QTime, Signal, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush, QPainter, QFontDatabase, QIcon, QPen, QPainterPath, QRadialGradient
import math
import random
import json
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


# ============ 1. SUPERCLASS (ABSTRACT BASE CLASS) ============
class TimerMode(ABC):
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
        return "🎉 Great job! You completed a Pomodoro!\nTime for a well-deserved break ☕"

    def get_style(self):
        return "color: #e94560; font-size: 15px; font-weight: bold; letter-spacing: 3px;"

    def get_random_quote(self):
        return random.choice(self._quote_list)


class BreakMode(TimerMode):
    def __init__(self):
        super().__init__("Break Time", 5, "#4ade80", "☕")
        self._relax_tips = ["Stretch your legs!", "Drink some water!", "Look away from screen!"]

    def get_message(self):
        return "💪 Break's over!\nReady to crush your next Pomodoro?"

    def get_style(self):
        return "color: #4ade80; font-size: 15px; font-weight: bold; letter-spacing: 3px;"

    def get_random_tip(self):
        return random.choice(self._relax_tips)


class LongBreakMode(TimerMode):
    def __init__(self):
        super().__init__("Long Break", 15, "#facc15", "🌟")

    def get_message(self):
        return "✨ Amazing! You completed 4 Pomodoros!\nEnjoy your long break 🎉"

    def get_style(self):
        return "color: #facc15; font-size: 15px; font-weight: bold; letter-spacing: 3px;"


# ============ 3. STATISTICS MANAGER ============
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


# ============ 4. CUSTOM WIDGETS ============
class Card(QFrame):
    def __init__(self, parent=None, accent=False):
        super().__init__(parent)
        border_color = "rgba(233,69,96,0.4)" if accent else "rgba(255,255,255,0.07)"
        self.setStyleSheet(f"""
            Card {{
                background: rgba(255,255,255,0.04);
                border: 1px solid {border_color};
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def setValue(self, value):
        self.animation.stop()
        self.animation.setEndValue(value)
        self.animation.start()


class PieChartWidget(QWidget):
    def __init__(self, focus_time, break_time, parent=None):
        super().__init__(parent)
        self.focus_time = focus_time
        self.break_time = break_time
        self.setMinimumHeight(220)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        total = self.focus_time + self.break_time
        w, h = self.width(), self.height()
        cx, cy = w // 2 - 60, h // 2
        radius = min(w, h) // 2 - 20

        if total == 0:
            painter.setPen(QColor(80, 80, 80))
            painter.setBrush(QColor(40, 40, 60))
            painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(cx - radius, cy - radius, radius * 2, radius * 2,
                             Qt.AlignCenter, "No data yet")
            return

        focus_angle = int((self.focus_time / total) * 360 * 16)
        break_angle = 360 * 16 - focus_angle

        painter.setPen(Qt.NoPen)

        g1 = QLinearGradient(cx - radius, cy - radius, cx + radius, cy + radius)
        g1.setColorAt(0, QColor(233, 69, 96))
        g1.setColorAt(1, QColor(255, 120, 120))
        painter.setBrush(g1)
        painter.drawPie(cx - radius, cy - radius, radius * 2, radius * 2, 90 * 16, -focus_angle)

        g2 = QLinearGradient(cx - radius, cy - radius, cx + radius, cy + radius)
        g2.setColorAt(0, QColor(74, 222, 128))
        g2.setColorAt(1, QColor(34, 197, 94))
        painter.setBrush(g2)
        painter.drawPie(cx - radius, cy - radius, radius * 2, radius * 2,
                        90 * 16 - focus_angle, -break_angle)

        hole = int(radius * 0.55)
        painter.setBrush(QColor(18, 18, 32))
        painter.drawEllipse(cx - hole, cy - hole, hole * 2, hole * 2)

        # Legend on right
        lx = cx + radius + 25
        ly = cy - 30

        painter.setBrush(QColor(233, 69, 96))
        painter.drawRoundedRect(lx, ly, 14, 14, 4, 4)
        painter.setPen(QColor(220, 220, 220))
        painter.setFont(QFont("Segoe UI", 10))
        fp = round((self.focus_time / total) * 100, 1)
        painter.drawText(lx + 20, ly + 12, f"Focus  {fp}%")

        ly += 30
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(74, 222, 128))
        painter.drawRoundedRect(lx, ly, 14, 14, 4, 4)
        painter.setPen(QColor(220, 220, 220))
        bp = round((self.break_time / total) * 100, 1)
        painter.drawText(lx + 20, ly + 12, f"Break  {bp}%")


# ============ 5. CIRCULAR PROGRESS WIDGET ============
class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 100
        self._color = QColor(233, 69, 96)
        self._bg_color = QColor(40, 40, 60)
        self.setFixedSize(240, 240)

    def setProgress(self, value):
        self._progress = value
        self.update()

    def setColor(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        pen_width = 14
        radius = min(w, h) // 2 - pen_width - 4

        # Track ring
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.NoBrush)
        track_pen = QPen(QColor(50, 50, 70), pen_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Progress arc
        angle = int((self._progress / 100) * 360 * 16)
        gradient = QLinearGradient(0, 0, w, h)
        lighter = self._color.lighter(130)
        gradient.setColorAt(0, lighter)
        gradient.setColorAt(1, self._color)
        progress_pen = QPen(QBrush(gradient), pen_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 90 * 16, -angle)

        # Inner glow dot at tip
        if self._progress > 1:
            tip_angle_rad = math.radians(90 - (self._progress / 100) * 360)
            dot_x = cx + radius * math.cos(tip_angle_rad)
            dot_y = cy - radius * math.sin(tip_angle_rad)
            glow_pen = QPen(Qt.NoPen)
            painter.setPen(glow_pen)
            painter.setBrush(lighter)
            painter.drawEllipse(int(dot_x) - 5, int(dot_y) - 5, 10, 10)


# ============ 6. STATISTICS DIALOG ============
class StatisticsDialog(QDialog):
    def __init__(self, stats_manager, parent=None):
        super().__init__(parent)
        self.stats = stats_manager
        self.setWindowTitle("Statistics")
        self.setMinimumSize(660, 680)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._setup_ui()
        self._animate_in()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #12121f;
                border: 1px solid rgba(233,69,96,0.35);
                border-radius: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 20)
        container.setGraphicsEffect(shadow)

        root = QVBoxLayout(container)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # ── Header ──
        hdr = QHBoxLayout()
        icon_lbl = QLabel("📊")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        title_lbl = QLabel("STATISTICS")
        title_lbl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #e94560; letter-spacing: 4px;")
        hdr.addWidget(icon_lbl)
        hdr.addSpacing(8)
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(233,69,96,0.15);
                border: 1.5px solid rgba(233,69,96,0.5);
                border-radius: 18px;
                color: #e94560;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #e94560; color: white; }
        """)
        close_btn.clicked.connect(self.accept)
        hdr.addWidget(close_btn)
        root.addLayout(hdr)

        # ── Divider ──
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background: rgba(255,255,255,0.07); max-height: 1px;")
        root.addWidget(div)

        # ── Scroll area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.04);
                width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(233,69,96,0.6);
                border-radius: 3px;
                min-height: 30px;
            }
        """)
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(sw)
        sl.setSpacing(16)
        sl.setContentsMargins(0, 0, 6, 0)

        # ── Stat cards row ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        streak = self._get_current_streak()
        avg = round(self.stats.total_pomodoros / max(1, len(self.stats._daily_stats)), 1)

        cards_row.addWidget(self._stat_card("🍅", "TOTAL", str(self.stats.total_pomodoros), "#e94560"))
        cards_row.addWidget(self._stat_card("⏱", "HOURS", str(self.stats.total_focus_hours), "#4ade80"))
        cards_row.addWidget(self._stat_card("📈", "AVG/DAY", str(avg), "#facc15"))
        cards_row.addWidget(self._stat_card("🔥", "STREAK", str(streak), "#fb923c"))
        sl.addLayout(cards_row)

        # ── Weekly bar chart ──
        week_card = Card()
        wl = QVBoxLayout(week_card)
        wl.setContentsMargins(18, 16, 18, 16)
        wl.setSpacing(10)

        week_hdr = QHBoxLayout()
        wt = QLabel("📈  WEEKLY OVERVIEW")
        wt.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        wt.setStyleSheet("color: #e0e0e0; letter-spacing: 1px;")
        week_hdr.addWidget(wt)
        week_hdr.addStretch()
        total_week = sum(d['count'] for d in self.stats.get_last_7_days())
        badge = QLabel(f"  🔥 {total_week} this week  ")
        badge.setStyleSheet("""
            background: rgba(233,69,96,0.18);
            color: #e94560;
            border: 1px solid rgba(233,69,96,0.4);
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 0;
        """)
        week_hdr.addWidget(badge)
        wl.addLayout(week_hdr)

        weekly_data = self.stats.get_last_7_days()
        max_count = max((d['count'] for d in weekly_data), default=1) or 1
        today_str = datetime.now().strftime("%a")

        for d in weekly_data:
            row = QHBoxLayout()
            row.setSpacing(10)

            day_lbl = QLabel(d['date'])
            day_lbl.setFixedWidth(38)
            day_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            is_today = (d['date'] == today_str)
            day_lbl.setStyleSheet(f"""
                color: {'#e94560' if is_today else '#888'};
                font-size: 11px;
                font-weight: {'bold' if is_today else 'normal'};
            """)

            bar = AnimatedProgressBar()
            bar.setRange(0, max(1, max_count))
            bar.setValue(d['count'])
            bar.setFormat(f"  {d['count']} 🍅" if d['count'] > 0 else "")
            bar.setTextVisible(True)
            bar.setFixedHeight(28)
            bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.06);
                    color: rgba(255,255,255,0.8);
                    font-size: 11px;
                    font-weight: bold;
                    text-align: left;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #c73b54, stop:1 #e94560);
                    border-radius: 8px;
                }
            """)
            row.addWidget(day_lbl)
            row.addWidget(bar)
            wl.addLayout(row)

        sl.addWidget(week_card)

        # ── Pie chart ──
        pie_card = Card()
        pl = QVBoxLayout(pie_card)
        pl.setContentsMargins(18, 16, 18, 16)
        pt = QLabel("🥧  TIME DISTRIBUTION")
        pt.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pt.setStyleSheet("color: #e0e0e0; letter-spacing: 1px;")
        pl.addWidget(pt)
        pie = PieChartWidget(self.stats.total_focus_time, self.stats.total_break_time)
        pie.setMinimumHeight(220)
        pl.addWidget(pie)
        sl.addWidget(pie_card)

        # ── Achievements ──
        ach_card = Card()
        al = QVBoxLayout(ach_card)
        al.setContentsMargins(18, 16, 18, 16)
        al.setSpacing(10)
        at = QLabel("🏆  ACHIEVEMENTS")
        at.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        at.setStyleSheet("color: #e0e0e0; letter-spacing: 1px;")
        al.addWidget(at)
        grid = QGridLayout()
        grid.setSpacing(8)
        for i, a in enumerate(self._get_achievements()):
            grid.addWidget(self._achievement_badge(a['icon'], a['title'], a['unlocked']), i // 2, i % 2)
        al.addLayout(grid)
        sl.addWidget(ach_card)

        # ── Quote ──
        quote_card = Card()
        ql = QVBoxLayout(quote_card)
        ql.setContentsMargins(22, 18, 22, 18)
        qlbl = QLabel(f'"{self._get_motivational_quote()}"')
        qlbl.setWordWrap(True)
        qlbl.setAlignment(Qt.AlignCenter)
        qlbl.setStyleSheet("color: #888; font-size: 12px; font-style: italic; line-height: 1.5;")
        ql.addWidget(qlbl)
        sl.addWidget(quote_card)

        scroll.setWidget(sw)
        root.addWidget(scroll)
        outer.addWidget(container)

    def _stat_card(self, icon, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        icon_lbl.setAlignment(Qt.AlignCenter)

        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(f"color: {color};")

        lbl_lbl = QLabel(label)
        lbl_lbl.setFont(QFont("Segoe UI", 9))
        lbl_lbl.setAlignment(Qt.AlignCenter)
        lbl_lbl.setStyleSheet("color: #666; letter-spacing: 1px;")

        layout.addWidget(icon_lbl)
        layout.addWidget(val_lbl)
        layout.addWidget(lbl_lbl)
        return card

    def _achievement_badge(self, icon, title, unlocked):
        w = QFrame()
        if unlocked:
            w.setStyleSheet("""
                QFrame {
                    background: rgba(250,204,21,0.08);
                    border: 1px solid rgba(250,204,21,0.35);
                    border-radius: 10px;
                }
            """)
        else:
            w.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.02);
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 10px;
                }
            """)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        il = QLabel(icon if unlocked else "🔒")
        il.setFont(QFont("Segoe UI Emoji", 16))
        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 10))
        tl.setStyleSheet(f"color: {'#facc15' if unlocked else '#444'};")

        layout.addWidget(il)
        layout.addWidget(tl)
        layout.addStretch()

        if unlocked:
            ck = QLabel("✓")
            ck.setStyleSheet("color: #4ade80; font-size: 14px; font-weight: bold;")
            layout.addWidget(ck)
        return w

    def _get_achievements(self):
        total = self.stats.total_pomodoros
        streak = self._get_current_streak()
        return [
            {'icon': '🍅', 'title': 'First Pomodoro', 'unlocked': total >= 1},
            {'icon': '🌟', 'title': 'Rookie  —  5 Pomodoros', 'unlocked': total >= 5},
            {'icon': '🎯', 'title': 'Consistent  —  10 Pomodoros', 'unlocked': total >= 10},
            {'icon': '💪', 'title': 'Warrior  —  20 Pomodoros', 'unlocked': total >= 20},
            {'icon': '🏆', 'title': 'Elite  —  50 Pomodoros', 'unlocked': total >= 50},
            {'icon': '👑', 'title': 'Legend  —  100 Pomodoros', 'unlocked': total >= 100},
            {'icon': '🔥', 'title': '3-Day Streak', 'unlocked': streak >= 3},
            {'icon': '⚡', 'title': '7-Day Streak', 'unlocked': streak >= 7},
        ]

    def _get_current_streak(self):
        streak = 0
        for i in range(30):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if self.stats._daily_stats.get(d, {}).get('pomodoros', 0) > 0:
                streak += 1
            else:
                break
        return streak

    def _get_motivational_quote(self):
        quotes = [
            "The secret of getting ahead is getting started.  — Mark Twain",
            "Small daily improvements are the key to staggering long-term results.",
            "The future depends on what you do today.  — Mahatma Gandhi",
            "You don't have to be great to start, but you have to start to be great.",
            "Your only limit is your mind. Keep pushing forward!",
        ]
        return random.choice(quotes)

    def _animate_in(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(220)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self._anim = anim


# ============ 7. MODE SELECTOR TABS ============
class ModeTab(QPushButton):
    def __init__(self, label, color, parent=None):
        super().__init__(label, parent)
        self._color = color
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self._apply_style(False)

    def _apply_style(self, active):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self._color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 16px;
                    letter-spacing: 1px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.05);
                    color: #777;
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 16px;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.09);
                    color: #bbb;
                }}
            """)

    def setChecked(self, checked):
        super().setChecked(checked)
        self._apply_style(checked)


# ============ 8. MAIN APPLICATION ============
class PomodoroTimer(QMainWindow):
    mode_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(480, 720)

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
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────
        topbar = QHBoxLayout()
        topbar.setSpacing(0)

        # App title
        app_title = QLabel("🍅 POMODORO")
        app_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #e94560; letter-spacing: 3px;")
        topbar.addWidget(app_title)
        topbar.addStretch()

        # Counter pills
        self.total_pill = self._pill("🍅", str(self._stats.total_pomodoros), "#e94560")
        self.today_pill = self._pill("📅", str(self._stats.today_pomodoros), "#4ade80")
        topbar.addWidget(self.total_pill)
        topbar.addSpacing(8)
        topbar.addWidget(self.today_pill)
        topbar.addSpacing(12)

        self.stats_btn = QPushButton("STATS")
        self.stats_btn.setFixedHeight(34)
        self.stats_btn.setCursor(Qt.PointingHandCursor)
        self.stats_btn.setStyleSheet("""
            QPushButton {
                background: rgba(233,69,96,0.15);
                border: 1.5px solid rgba(233,69,96,0.5);
                border-radius: 10px;
                color: #e94560;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background: #e94560;
                color: white;
            }
        """)
        self.stats_btn.clicked.connect(self._show_statistics)
        topbar.addWidget(self.stats_btn)

        root.addLayout(topbar)
        root.addSpacing(20)

        # ── Mode tabs ──────────────────────────────────────────────
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(6)

        self.tab_work = ModeTab("Focus", "#e94560")
        self.tab_break = ModeTab("Break", "#4ade80")
        self.tab_long = ModeTab("Long Break", "#facc15")

        self.tab_work.setChecked(True)
        self.tab_work.clicked.connect(lambda: self._select_mode(0))
        self.tab_break.clicked.connect(lambda: self._select_mode(1))
        self.tab_long.clicked.connect(lambda: self._select_mode(2))

        tabs_layout.addWidget(self.tab_work)
        tabs_layout.addWidget(self.tab_break)
        tabs_layout.addWidget(self.tab_long)
        root.addLayout(tabs_layout)
        root.addSpacing(28)

        # ── Timer card ──────────────────────────────────────────────
        timer_card = QFrame()
        timer_card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 28px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 12)
        timer_card.setGraphicsEffect(shadow)

        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(28, 30, 28, 30)
        timer_layout.setSpacing(0)
        timer_layout.setAlignment(Qt.AlignCenter)

        # Progress ring
        self.circular_progress = CircularProgress()
        timer_layout.addWidget(self.circular_progress, alignment=Qt.AlignCenter)

        # Overlay time display inside ring — positioned via stack
        self.timer_display = QLabel("25:00")
        self.timer_display.setAlignment(Qt.AlignCenter)
        self.timer_display.setFont(QFont("Segoe UI", 46, QFont.Weight.Bold))
        self.timer_display.setStyleSheet("color: #ffffff; letter-spacing: -2px;")

        self.mode_label = QLabel()
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #555; font-size: 11px;")
        self.message_label.setMaximumWidth(320)

        timer_layout.addSpacing(12)
        timer_layout.addWidget(self.timer_display, alignment=Qt.AlignCenter)
        timer_layout.addSpacing(4)
        timer_layout.addWidget(self.mode_label, alignment=Qt.AlignCenter)
        timer_layout.addSpacing(8)
        timer_layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        root.addWidget(timer_card)
        root.addSpacing(24)

        # ── Pomodoro dots ──────────────────────────────────────────
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(8)
        dots_layout.setAlignment(Qt.AlignCenter)

        self.pom_dots = []
        for i in range(4):
            dot = QLabel("○")
            dot.setFont(QFont("Segoe UI", 18))
            dot.setAlignment(Qt.AlignCenter)
            dot.setStyleSheet("color: rgba(255,255,255,0.15);")
            self.pom_dots.append(dot)
            dots_layout.addWidget(dot)

        root.addLayout(dots_layout)
        root.addSpacing(22)

        # ── Controls ──────────────────────────────────────────────
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.reset_btn = self._icon_btn("⟳", "rgba(255,255,255,0.06)", "#888")
        self.start_btn = self._main_btn("▶  START")
        self.skip_btn = self._icon_btn("⏭", "rgba(255,255,255,0.06)", "#888")

        self.pause_btn = self._main_btn("⏸  PAUSE")
        self.pause_btn.setVisible(False)

        controls.addWidget(self.reset_btn)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.skip_btn)
        root.addLayout(controls)

        root.addStretch()

        self.start_btn.clicked.connect(self._start_timer)
        self.pause_btn.clicked.connect(self._pause_timer)
        self.reset_btn.clicked.connect(self._reset_timer)
        self.skip_btn.clicked.connect(self._skip_mode)

    # ── Widget factories ──────────────────────────────────────────
    def _pill(self, icon, text, color):
        w = QLabel(f"{icon} {text}")
        w.setStyleSheet(f"""
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            color: #ccc;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 12px;
        """)
        return w

    def _icon_btn(self, icon, bg, color):
        btn = QPushButton(icon)
        btn.setFixedSize(52, 52)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI Emoji", 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                color: {color};
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.10);
                color: #ddd;
            }}
        """)
        return btn

    def _main_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(52)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #c73b54, stop:1 #e94560);
                color: white;
                border: none;
                border-radius: 16px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #e94560, stop:1 #ff6b6b);
            }
            QPushButton:pressed { background: #c73b54; }
        """)
        return btn

    def _set_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #0d0d1a;
            }
            QWidget {
                background: transparent;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { background: transparent; }
        """)

    def _select_mode(self, idx):
        tabs = [self.tab_work, self.tab_break, self.tab_long]
        for i, tab in enumerate(tabs):
            tab.setChecked(i == idx)
        self._timer.stop()
        self._is_running = False
        self._show_start()
        self.current_mode = self.modes[idx]

    def _update_dots(self):
        filled = self._pomodoro_count % 4
        for i, dot in enumerate(self.pom_dots):
            if i < filled:
                dot.setText("●")
                dot.setStyleSheet("color: #e94560; font-size: 18px;")
            else:
                dot.setText("○")
                dot.setStyleSheet("color: rgba(255,255,255,0.15); font-size: 18px;")

    def _update_message(self):
        if isinstance(self._current_mode, WorkMode):
            self.message_label.setText(f'"{self._current_mode.get_random_quote()}"')
        elif isinstance(self._current_mode, BreakMode):
            self.message_label.setText(self._current_mode.get_random_tip())
        else:
            self.message_label.setText("Take a well-deserved long break 🌟")

    def _on_mode_changed(self, mode):
        self.mode_label.setText(mode.name.upper())
        self.mode_label.setStyleSheet(mode.get_style())
        self.circular_progress.setColor(QColor(mode.color))
        self._update_message()
        self._update_display()

        # Sync tabs
        idx = self.modes.index(mode)
        tabs = [self.tab_work, self.tab_break, self.tab_long]
        for i, tab in enumerate(tabs):
            tab.setChecked(i == idx)

    def _update_display(self):
        m = self._time_left // 60
        s = self._time_left % 60
        self.timer_display.setText(f"{m:02d}:{s:02d}")
        total = self._current_mode.duration * 60
        pct = (self._time_left / total) * 100 if total > 0 else 0
        self.circular_progress.setProgress(pct)

    def _update_timer(self):
        if self._time_left > 0:
            self._time_left -= 1
            self._update_display()
        else:
            self._timer.stop()
            self._is_running = False
            self._show_start()

            if isinstance(self._current_mode, WorkMode):
                self._stats.add_pomodoro(self._current_mode.duration)
                self._pomodoro_count += 1
                self._update_counters()
                self._update_dots()
            else:
                self._stats.add_break(self._current_mode.duration)

            msg = QMessageBox(self)
            msg.setWindowTitle("Timer Complete!")
            msg.setText(self._current_mode.get_message())
            msg.setIcon(QMessageBox.Information)
            msg.exec()

            if isinstance(self._current_mode, WorkMode):
                next_idx = 2 if self._pomodoro_count % 4 == 0 else 1
            else:
                next_idx = 0
            self.current_mode = self.modes[next_idx]
            self._update_display()

    def _update_counters(self):
        self.total_pill.setText(f"🍅 {self._stats.total_pomodoros}")
        self.today_pill.setText(f"📅 {self._stats.today_pomodoros}")

    def _show_start(self):
        self.start_btn.setVisible(True)
        self.pause_btn.setVisible(False)

    def _show_pause(self):
        self.start_btn.setVisible(False)
        self.pause_btn.setVisible(True)

    def _start_timer(self):
        if not self._is_running:
            self._timer.start(1000)
            self._is_running = True
            self._show_pause()

    def _pause_timer(self):
        if self._is_running:
            self._timer.stop()
            self._is_running = False
            self._show_start()
            self.start_btn.setText("▶  RESUME")

    def _reset_timer(self):
        self._timer.stop()
        self._is_running = False
        self.start_btn.setText("▶  START")
        self._show_start()
        self.current_mode = self.modes[0]

    def _skip_mode(self):
        self._timer.stop()
        self._is_running = False
        self._show_start()
        self.start_btn.setText("▶  START")

        if isinstance(self._current_mode, WorkMode):
            next_idx = 2 if self._pomodoro_count % 4 == 3 else 1
        else:
            next_idx = 0
        self.current_mode = self.modes[next_idx]
        self._update_display()

    def _show_statistics(self):
        dialog = StatisticsDialog(self._stats, self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec())
