from django.contrib import admin
from .models import Course, Module, Quiz, Question, ModuleFile


# --------------------------
# Inline for multiple files
# --------------------------
class ModuleFileInline(admin.TabularInline):
    model = ModuleFile
    extra = 1
    fields = ("file",)


# --------------------------
# Inline for Modules under Course
# --------------------------
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title", "description", "video_url", "video")
    show_change_link = True  # allow clicking into module admin page


# --------------------------
# Course Admin
# --------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "ship_type")
    list_filter = ("ship_type", "positions")
    search_fields = ("title", "description")
    inlines = [ModuleInline]


# --------------------------
# Module Admin
# --------------------------
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    search_fields = ("title", "description")
    list_filter = ("course",)
    fields = ("course", "title", "description", "video_url", "video")   # NEW
    inlines = [ModuleFileInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 2


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "module")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "quiz", "correct_answer")
    search_fields = ("question_text",)
    list_filter = ("quiz", "correct_answer")
