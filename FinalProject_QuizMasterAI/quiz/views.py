from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from .models import User, Topic, UserTopicProgress, Quiz, Question, Answer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Avg, Max, Q
import requests
import json

def landing_page(request):
    """Render the landing page."""
    return render(request, 'quiz/landing_page.html')

def login_view(request):
    """Handle user login and authentication."""
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("topic_list"))
        else:
            return render(request, "quiz/login.html", {
                "message": "Invalid email and/or password."
            })
    return render(request, "quiz/login.html")

def register(request):
    """Handle user registration and account creation."""
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        if password != confirmation:
            return render(request, "quiz/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "quiz/register.html", {
                "message": "Email address already taken."
            })
            
        login(request, user)
        return HttpResponseRedirect(reverse("topic_list"))
    return render(request, "quiz/register.html")

def logout_view(request):
    """Log the user out and redirect to the landing page."""
    logout(request)
    return HttpResponseRedirect(reverse("landing"))

@login_required
def user_profile(request):
    """Display the user's profile including quiz history and statistics."""
    # Get user's quiz history
    quiz_history = Quiz.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate overall statistics
    total_quizzes = quiz_history.count()  # Using count() method instead of Count
    avg_score = quiz_history.aggregate(Avg('score'))['score__avg'] or 0
    
    # Get progress by topic with proper counting
    topic_progress = UserTopicProgress.objects.filter(user=request.user).select_related('topic')
    
    # Calculate achievements with correct aggregation
    achievements = {
        'topics_attempted': topic_progress.count(),
        'topics_mastered': topic_progress.filter(best_score__gte=80).count(),
        'perfect_scores': quiz_history.filter(score=100).count(),
        'total_questions': Question.objects.filter(quiz__user=request.user).count()
    }
    
    # Get recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_activity = (
        quiz_history.filter(created_at__gte=thirty_days_ago)
        .values('created_at__date')  # Group by date
        .annotate(
            count=Count('id'),
            avg_score=Avg('score')
        )
        .order_by('created_at__date')
    )
    
    # Calculate improvement metrics
    first_five_avg = (
        quiz_history.order_by('created_at')[:5]
        .aggregate(Avg('score'))['score__avg'] or 0
    )
    
    last_five_avg = (
        quiz_history.order_by('-created_at')[:5]
        .aggregate(Avg('score'))['score__avg'] or 0
    )
    
    improvement = last_five_avg - first_five_avg

    context = {
        'quiz_history': quiz_history[:10],  # Last 10 quizzes
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'topic_progress': topic_progress,
        'achievements': achievements,
        'recent_activity': recent_activity,
        'improvement': improvement,
        'strongest_topic': topic_progress.order_by('-best_score').first(),
        'needs_improvement': topic_progress.order_by('best_score').first()
    }
    
    return render(request, 'quiz/profile.html', context)

############################################################

#Quiz functionality
@login_required
def topic_list(request):
    """List available topics with filtering and pagination."""
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    
     # Filter topics based on category
    if category_filter == 'all':
        topics = Topic.objects.all()
    else:
        topics = Topic.objects.filter(category=category_filter)

    # Further filter topics based on search query
    if search_query:
        topics = topics.filter(name__icontains=search_query)

    topics = topics.order_by('category', 'name')

    categories = Topic.objects.values_list('category', flat=True).distinct()

    # Pagination
    paginator = Paginator(topics, 12)  # Set to 12 topics per page
    page = request.GET.get('page', 1)
    
    try:
        topics_page = paginator.get_page(page)
    except PageNotAnInteger:
        topics_page = paginator.get_page(1)
    except EmptyPage:
        topics_page = paginator.get_page(paginator.num_pages)
    
    # Add user progress to topics
    for topic in topics_page:
        try:
            topic.user_progress = UserTopicProgress.objects.get(user=request.user, topic=topic)
        except UserTopicProgress.DoesNotExist:
            topic.user_progress = None
    
    return render(request, 'quiz/topic_list.html', {
        'topics': topics_page,  # Pass the paginated topics to the template
        'categories': categories,
        'topics_page': topics_page
    })

@login_required
def start_quiz(request, topic_id):
    """Start a new quiz for the selected topic."""

    # Get the requested topic or return 404 if not found
    topic = get_object_or_404(Topic, id=topic_id)
    
    try:
        # Get or create user's progress record for this topic
        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
            defaults={
                'attempts': 0,
                'best_score': 0
            }
        )
        
        # Check if user has attempts remaining
        if not progress.can_attempt_quiz():
            messages.error(
                request, 
                f"You've reached the maximum attempts ({topic.max_attempts}) for this topic."
                f"Your best score was {progress.best_score}%."
            )
            return redirect('topic_list')
        
        # Create a new quiz instance
        quiz = Quiz.objects.create(
            user=request.user,
            topic=topic,
            score=0  # Initialize score to 0
        )
        
        # Generate questions using AI
        questions = generate_quiz_questions(topic.name)
        
        if not questions:
            raise ValueError("No questions were generated")
        
        # Create question and answer records in the database
        for q_data in questions:
            # Create the question
            question = Question.objects.create(
                quiz=quiz,
                text=q_data['question'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation']
            )
            
            # Create the answers for this question
            for a_data in q_data['answers']:
                Answer.objects.create(
                    question=question,
                    text=a_data['text'],
                    is_correct=a_data['is_correct']
                )
        
        # Update the user's attempt counter
        progress.attempts += 1
        progress.save()
        
        # Initialize session variable to track answered questions
        request.session[f'quiz_{quiz.id}_answered'] = []
        
        # If everything succeeded, redirect to the first question
        return redirect('quiz_question', quiz_id=quiz.id)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating quiz: {str(e)}")
        
        # Clean up if quiz was created but something went wrong
        if 'quiz' in locals():
            quiz.delete()
        
        # Show error message to user
        messages.error(
            request, 
            "Failed to create quiz. Please try again or contact support if the problem persists."
        )
        return redirect('topic_list')

def generate_quiz_questions(topic):
    """Generate quiz questions using an external API."""

    OLLAMA_URL = "http://localhost:11434/api/generate"
    
    # Structured prompt to get consistent response format
    prompt = f"""Generate 5 multiple choice questions about {topic}.
    Return only valid JSON in this exact format, with no additional text:
    {{
        "questions": [
            {{
                "question": "Write the question here?",
                "answers": [
                    {{"text": "Correct answer", "is_correct": true}},
                    {{"text": "Wrong answer 1", "is_correct": false}},
                    {{"text": "Wrong answer 2", "is_correct": false}},
                    {{"text": "Wrong answer 3", "is_correct": false}}
                ],
                "explanation": "Explain why the correct answer is right"
            }}
        ]
    }}"""

    try:
        # Make API request with timeout
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3", # Name of the model. Can be change depending of your needed and the power of your machine 
                "prompt": prompt,
                "stream": False  # Important: disable streaming for proper JSON response
            },
            timeout=30  # Add timeout to prevent hanging(consider increase it according to the response time of the model)
        )
        
        # Debug logging
        print("API Response:", response.text[:200])  # Print first 200 chars for debugging
        
        # Parse the response carefully
        try:
            response_data = response.json()
            # Extract the actual JSON string from the response
            response_text = response_data.get('response', '{}')
            
            # Find the JSON object within the response text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON object found in response")
                
            questions = questions_data.get('questions', [])
            
            # Validate and format each question
            formatted_questions = []
            for q in questions:
                # Find the correct answer
                correct_answer = next(
                    (a['text'] for a in q['answers'] if a['is_correct']),
                    None
                )
                
                if not correct_answer:
                    continue  # Skip invalid questions
                    
                formatted_questions.append({
                    'question': q['question'],
                    'answers': q['answers'],
                    'correct_answer': correct_answer,
                    'explanation': q.get('explanation', 'No explanation provided')
                })
            
            if not formatted_questions:
                raise ValueError("No valid questions generated")
                
            return formatted_questions
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            raise
            
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        # Return fallback questions
        return [
            {
                'question': f'What is an important concept in {topic}?',
                'answers': [
                    {'text': 'This is the correct answer', 'is_correct': True},
                    {'text': 'First incorrect option', 'is_correct': False},
                    {'text': 'Second incorrect option', 'is_correct': False},
                    {'text': 'Third incorrect option', 'is_correct': False}
                ],
                'correct_answer': 'This is the correct answer',
                'explanation': 'This is a fallback question due to API error.'
            }
        ]

@login_required
def quiz_question(request, quiz_id):
    """Display the current quiz question and handle user answers."""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    # Get answered questions from session
    answered_questions = request.session.get(f'quiz_{quiz_id}_answered', [])
    
    # Get all questions in a fixed order
    all_questions = list(quiz.question_set.all().order_by('id'))
    total_questions = len(all_questions)
    
    # Get remaining questions
    remaining_questions = [q for q in all_questions if q.id not in answered_questions]
    
    if not remaining_questions:
        return redirect('quiz_results', quiz_id=quiz.id)
    
    current_question = remaining_questions[0]
    
    # Find current question number by its position in all_questions
    current_question_number = all_questions.index(current_question) + 1
    
    # Calculate progress
    progress = ((current_question_number) / total_questions) * 100

    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        if answer_id:
            selected_answer = get_object_or_404(Answer, id=answer_id)
            correct_answer = current_question.answer_set.get(is_correct=True)
            
            # Update quiz score if correct
            if selected_answer.is_correct:
                quiz.score += 1
                quiz.save()
            
            # Mark question as answered
            if current_question.id not in answered_questions:
                answered_questions.append(current_question.id)
                request.session[f'quiz_{quiz_id}_answered'] = answered_questions
            
            return render(request, 'quiz/feedback.html', {
                'quiz': quiz,
                'question': current_question,
                'selected_answer': selected_answer,
                'correct_answer': correct_answer,
                'is_correct': selected_answer.is_correct,
                'next_question': len(remaining_questions) > 1,
                'current_question_number': current_question_number,
                'total_questions': total_questions,
                'progress': progress
            })
    
    return render(request, 'quiz/quiz_question.html', {
        'quiz': quiz,
        'question': current_question,
        'progress': progress,
        'total_questions': total_questions,
        'current_question_number': current_question_number
    })

@login_required
def quiz_feedback(request, quiz_id, question_id):
    """Provide feedback on the user's answer to the current question."""
    question = get_object_or_404(Question, id=question_id)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get next question if it exists
    next_question = quiz.question_set.filter(id__gt=question_id).first()
    
    return render(request, 'quiz/feedback.html', {
        'question': question,
        'quiz': quiz,
        'next_question': next_question,
        'explanation': question.explanation
    })

@login_required
def quiz_results(request, quiz_id):
    """Display the results of the completed quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    total_questions = quiz.question_set.count()
    percentage = (quiz.score / total_questions) * 100 if total_questions > 0 else 0
    
    # Update user's best score if applicable
    progress = UserTopicProgress.objects.get(user=request.user, topic=quiz.topic)
    if percentage > progress.best_score:
        progress.best_score = percentage
        progress.save()
    
    return render(request, 'quiz/results.html', {
        'quiz': quiz,
        'total_questions': total_questions,
        'percentage': percentage,
        'attempts_remaining': quiz.topic.max_attempts - progress.attempts
    })

##############################################
@login_required
def leaderboard(request):
    """
    Leaderboard data including:
    - Overall top performers
    - Topic-specific rankings
    - User's personal standings
    """
    # Get the selected category
    category = request.GET.get('category', 'overall')
    
    # Get selected time period
    time_period = request.GET.get('period', 'all')
    
    # Base queryset for user progress
    base_query = UserTopicProgress.objects.select_related('user', 'topic')
    
    # Apply time period filter
    if time_period == 'month':
        base_query = base_query.filter(last_attempt__gte=timezone.now() - timezone.timedelta(days=30))
    elif time_period == 'week':
        base_query = base_query.filter(last_attempt__gte=timezone.now() - timezone.timedelta(days=7))
    
    # Calculate rankings based on category
    if category == 'overall':
        rankings = (
            base_query
            .values('user__username')
            .annotate(
                total_score=Avg('best_score'),
                quizzes_taken=Count('topic'),
                topics_mastered=Count('topic', filter=Q(best_score__gte=90)),
                avg_attempts=Avg('attempts')
            )
            .filter(total_score__isnull=False)  # Exclude users with no scores
            .order_by('-total_score')
        )
    else:
        # Topic-specific rankings
        rankings = (
            base_query
            .filter(topic__category=category)
            .values('user__username')
            .annotate(
                total_score=Avg('best_score'),
                quizzes_taken=Count('topic'),
                best_performance=Max('best_score')
            )
            .filter(total_score__isnull=False)  # Exclude users with no scores
            .order_by('-total_score')
        )
    
    # Get user's personal stats and ranking
    user_stats = get_user_ranking(request.user, base_query)
    
    # Get available categories for filtering
    categories = Topic.objects.values_list('category', flat=True).distinct()
    
    context = {
        'rankings': rankings[:50],  # Top 50 users
        'user_stats': user_stats,
        'categories': categories,
        'selected_category': category,
        'selected_period': time_period,
        'total_participants': UserTopicProgress.objects.values('user').distinct().count()
    }
    
    return render(request, 'quiz/leaderboard.html', context)

def get_user_ranking(user, base_query):
    """Helper function to get user's ranking and stats"""

    # Get user's average score
    user_avg_score = base_query.filter(user=user).aggregate(avg_score=Avg('best_score'))['avg_score']

    # If user has no scores yet, return default values
    if user_avg_score is None:
        return {
            'position': '-',  # Display dash instead of number
            'total_topics': 0,
            'avg_score': 0,
            'topics_mastered': 0,
            'has_activity': False  # Flag to indicate if user has any activity
        }

    # Calculate user position only if they have scores
    user_position = (
        base_query
        .values('user__username')
        .annotate(total_score=Avg('best_score'))
        .order_by('-total_score')
        .filter(total_score__gt=user_avg_score)
        .count() + 1
    )
    
    return {
        'position': user_position,
        'total_topics': base_query.filter(user=user).count(),
        'avg_score': user_avg_score or 0,
        'topics_mastered': base_query.filter(user=user, best_score__gte=90).count(),
        'has_activity': True
    }
