document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Submit handler
  document.querySelector("#compose-form").addEventListener("submit", Send_email);

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

function Send_email(event) {
  event.preventDefault();

  // Get the form data
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send the POST request to send the email
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    // Log the result for debugging
    console.log(result);
    
    // Load the sent mailbox after email is sent
    load_mailbox('sent');
  });
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-details-view').style.display = 'none';

  // Clear previous emails
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch emails for the selected mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const emailDiv = document.createElement('div');
      //change background-color
      emailDiv.className = email.read ? 'emailread' : 'emailunread';
      // Style
      emailDiv.innerHTML = `
      <ul class="email-list">
        <li class="email-item">
          <span>${email.sender}</span>
          <span class="subject">${email.subject}</span>
          <span class="timestamp">${email.timestamp}</span>
        </li>
      </ul>
      `;

      // Add event listener to view the email when clicked
      emailDiv.addEventListener('click', () => View_email(email.id));
      document.querySelector('#emails-view').append(emailDiv);
    });
  });
}

function View_email(id) {
  // Fetch email details
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    // Show the email view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#emails-details-view').style.display = 'block';

    // Display email details
    document.querySelector('#emails-details-view').innerHTML = `
        <b>From:</b> ${email.sender}<br>
        <b>To:</b> ${email.recipients.join(', ')}<br>
        <b>Subject:</b> ${email.subject}<br>
        <b>Timestamp:</b> ${email.timestamp}<br>
        <hr>
        ${email.body}
        <hr>`;

    // Mark the email as read
    if (!email.read) {
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ read: true })
      });
    }

    // Archive/Unarchive buttons
    const currentMailbox = document.querySelector('h3').innerText.toLowerCase();
    if (currentMailbox === 'inbox' || currentMailbox === 'archive') {
      const archiveButton = document.createElement('button');
      archiveButton.className = 'btn btn-secondary';
      archiveButton.innerHTML = email.archived ? 'Unarchive' : 'Archive';
      archiveButton.addEventListener('click', () => {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({ archived: !email.archived })
        })
        .then(() => load_mailbox('inbox'));
      });
      document.querySelector('#emails-details-view').append(archiveButton);
    }

    // Reply button for emails in the inbox
    if (currentMailbox === 'inbox') {
      const replyButton = document.createElement('button');
      replyButton.className = 'btn btn-primary';
      replyButton.innerHTML = 'Reply';
      replyButton.addEventListener('click', () => {
        compose_email();
        document.querySelector('#compose-recipients').value = email.sender;
        document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
        document.querySelector('#compose-body').value = `\n\n---\nOn ${email.timestamp}, ${email.sender} \n wrote:${email.body} \n`;
      });
      document.querySelector('#emails-details-view').append(replyButton);
    }


  });
}