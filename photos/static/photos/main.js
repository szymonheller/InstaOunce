function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

console.log("działa!")

const like_btn = document.querySelector('#like');
const dislike_btn = document.querySelector('#dislike');

console.log(like_btn)
console.log(dislike_btn)

function like_request(event) {
    const token = getCookie('csrftoken')
    console.log(token)
    fetch(event.target.dataset.url, {
        method: 'POST',
        mode: 'cors',
        body: '',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': token
        }
    }).then(data => {
        console.log(data)
        event.toggleClass('liked')
    })

}

like_btn.addEventListener('click', (like_request));

dislike_btn.addEventListener('click', (like_request));