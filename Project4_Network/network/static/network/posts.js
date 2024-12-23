document.addEventListener('DOMContentLoaded', function() {
    // listeners for edit buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const post = this.closest('.post');
            toggleEditMode(post);
        });
    });

    // listeners for save buttons
    document.querySelectorAll('.save-btn').forEach(button => {
        button.addEventListener('click', function() {
            const post = this.closest('.post');
            saveEdit(post);
        });
    });

    // listeners for cancel buttons
    document.querySelectorAll('.cancel-btn').forEach(button => {
        button.addEventListener('click', function() {
            const post = this.closest('.post');
            toggleEditMode(post);
        });
    });

    // listeners for like buttons
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const post = this.closest('.post');
            toggleLike(post);
        });
    });

    // Follow button listener
    const followBtn = document.querySelector('.follow-btn');
    if (followBtn) {
        followBtn.addEventListener('click', function() {
            toggleFollow(this);
        });
    }
});

function toggleEditMode(post) {
    const content = post.querySelector('.content');
    const editArea = post.querySelector('.edit-area');
    const editBtn = post.querySelector('.edit-btn');
    
    content.classList.toggle('d-none');
    editArea.classList.toggle('d-none');
    editBtn.classList.toggle('d-none');
}

async function saveEdit(post) {
    const postId = post.dataset.postId;
    const content = post.querySelector('.edit-area textarea').value;
    
    try {
        const response = await fetch(`/edit/${postId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                content: content
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const contentDiv = post.querySelector('.content');
        contentDiv.textContent = content;
        toggleEditMode(post);
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving edit. Please try again.');
    }
}

async function toggleLike(post) {
    const likeBtn = post.querySelector('.like-btn');
    const postId = likeBtn.dataset.postId;
    const likeCount = post.querySelector('.like-count');
    
    try {
        const response = await fetch(`/like/${postId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        likeCount.textContent = data.likes_count;
        if (data.liked) {
            likeBtn.classList.remove('btn-outline-danger');
            likeBtn.classList.add('btn-danger');
        } else {
            likeBtn.classList.remove('btn-danger');
            likeBtn.classList.add('btn-outline-danger');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating like status. Please try again.');
    }
}

async function toggleFollow(button) {
    const userId = button.dataset.userId;
    
    try {
        const response = await fetch(`/toggle_follow/${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        // button text and styling
        button.textContent = data.following ? 'Unfollow' : 'Follow';
        button.classList.toggle('btn-primary', !data.following);
        button.classList.toggle('btn-secondary', data.following);
        
        // followers count
        const followersCount = document.querySelector('.followers-count');
        if (followersCount) {
            followersCount.textContent = data.followers_count;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating follow status. Please try again.');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 