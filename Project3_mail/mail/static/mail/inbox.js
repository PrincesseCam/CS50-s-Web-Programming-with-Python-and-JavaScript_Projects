document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Submit handler
  document.querySelector("#compose-form").addEventListener("submit",Send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#emails-details-view').style.display = 'none';
  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function View_email(id){
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    // Print email
    console.log(email);
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#emails-details-view').style.display = 'block';
    
    document.querySelector('#emails-details-view').innerHTML = `
    <ul class="list-group">
      <li class="list-group-item"><strong>From:</strong> ${email.sender}</li>
      <li class="list-group-item"><strong>To:</strong> ${email.recipients}</li>
      <li class="list-group-item"><strong>Subject:</strong> ${email.subject}</li>
      <li class="list-group-item"><strong>Timestamp:</strong> ${email.timestamp}</li>
      <li class="list-group-item"> ${email.body}</li>
    </ul>
    `
//the email has been clicked on, you should mark the email as read. 
    if(!email.read){
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      })
    }
    // Archive/Unarchive
    const btn_arch = document.createElement('button');
    btn_arch.innerHTML = email.archived ? "Unarchive" : "Archive";
    btn_arch.className = email.archived ? "btn btn-danger" : "btn btn-success";
    btn_arch.addEventListener('click', function() {
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: !email.archived
        })
      })
      .then(() => {load_mailbox('archive')});
    });
    document.querySelector('#emails-details-view').append(btn_arch);    

    // Reply
    const btn_reply = document.createElement('button');
    btn_reply.innerHTML = "Reply";
    btn_reply.className = "btn btn-info";
    btn_reply.addEventListener('click', function() {
      compose_email();
      document.querySelector('#compose-recipients').value = 'email.sender';
      let subject = email.subject;
      if (subject.split('',1)[0] != "Re:"){
        subject = "Re:" + email.subject;
      }
      document.querySelector('#compose-subject').value = subject;
      document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;      
    });
    document.querySelector('#emails-details-view').append(btn_reply);    
});
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-details-view').style.display = 'none';
  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

// Get the email for that mailbox and user
fetch(`/emails/${mailbox}`)
.then(response => response.json())
.then(emails => {
    // Loop emails
    emails.forEach(singleEmail => {

      //create div for each email
      const newEmail = document.createElement('div');
      // Bootstrap for the className (need to make change and improve the style)
      newEmail.className = "List-group-item";
      newEmail.innerHTML = `
      <h1>Sender: ${singleEmail.sender}<h1>
      <h3>Subject: ${singleEmail.subject}<h3>
      <p>${singleEmail.timestamp}<p>
      `;
      //change background-color
      newEmail.className = singleEmail.read ? 'emailread': 'emailunread';
      // Add click event to view email
      newEmail.addEventListener('click', function() {
        View_email(singleEmail.id)});
      document.querySelector('#emails-view').append(newEmail);
    })
});

}

function Send_email(event) {
  event.preventDefault();

  // Store field
  const recipient = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  //send data to back end
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipient,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
  });
  localStorage.clear();
  load_mailbox('sent');
  return false;
}

