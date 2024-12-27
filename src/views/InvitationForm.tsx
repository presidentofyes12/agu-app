import React from 'react';
import './InvitationForm.css';
import { RouteComponentProps } from '@reach/router';

interface InvitationFormProps extends RouteComponentProps {}

const InvitationForm: React.FC<InvitationFormProps> = () => {
  React.useEffect(() => {
    const inviterForm = document.getElementById('inviter-form') as HTMLFormElement;
    const invitedSection = document.getElementById('invited-section') as HTMLElement;
    const invitedForm = document.getElementById('invited-form') as HTMLFormElement;

    const handleInviterSubmit = (event: Event) => {
      event.preventDefault();
      const formData = new FormData(inviterForm);
      const invitedData = {
        firstName: formData.get('first-name'),
        lastName: formData.get('last-name'),
        communicationChannel: formData.get('communication-channel'),
        ageRange: formData.get('age-range'),
        location: formData.get('location'),
        education: formData.get('education'),
        employment: formData.get('employment'),
        industry: formData.get('industry'),
        learningGoals: formData.get('learning-goals')
      };

      (document.getElementById('inv-first-name') as HTMLInputElement).value = invitedData.firstName as string;
      (document.getElementById('inv-last-name') as HTMLInputElement).value = invitedData.lastName as string;
      (document.getElementById('inv-communication-channel') as HTMLSelectElement).value = invitedData.communicationChannel as string;
      (document.getElementById('inv-age-range') as HTMLSelectElement).value = invitedData.ageRange as string;
      (document.getElementById('inv-location') as HTMLInputElement).value = invitedData.location as string;
      (document.getElementById('inv-education') as HTMLSelectElement).value = invitedData.education as string;
      (document.getElementById('inv-employment') as HTMLSelectElement).value = invitedData.employment as string;
      (document.getElementById('inv-industry') as HTMLInputElement).value = invitedData.industry as string;
      (document.getElementById('inv-learning-goals') as HTMLTextAreaElement).value = invitedData.learningGoals as string;

      invitedSection.style.display = 'block';
    };

    const handleInvitedSubmit = (event: Event) => {
      event.preventDefault();
      console.log('Invitation confirmed');
    };

    inviterForm.addEventListener('submit', handleInviterSubmit);
    invitedForm.addEventListener('submit', handleInvitedSubmit);

    return () => {
      inviterForm.removeEventListener('submit', handleInviterSubmit);
      invitedForm.removeEventListener('submit', handleInvitedSubmit);
    };
  }, []);

  return (
    <div>
      <header>
        <h1>Aspire, Grow, Unite</h1>
        <nav>
          <a href="/">Home</a>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
        </nav>
      </header>
      <main>
        <h2>Make Connections & Get Things Done</h2>
        <p>The all-in-one platform for staying informed, having fun, and making a difference.</p>
        <div className="sections">
          <div className="section">
            <img src="connect.png" alt="Connection Icon" />
            <h3>Engage & Connect</h3>
            <p>Share ideas, socialize, and build meaningful connections with people who share your interests.</p>
          </div>
          <div className="section">
            <img src="content.png" alt="Content Icon" />
            <h3>Learn & Be Entertained</h3>
            <p>Discover inspiring content, explore diverse topics, and develop new skills through engaging experiences.</p>
          </div>
          <div className="section">
            <img src="productivity.png" alt="Productivity Icon" />
            <h3>Shop, Manage & Access</h3>
            <p>Simplify tasks, manage finances, and access essential services - including jobs, rides, and bars.</p>
          </div>
        </div>
        <div className="questions">
          <h3>Inviter: Tell us about the person you're inviting:</h3>
          <form id="inviter-form">
            <label htmlFor="first-name">First Name:</label>
            <input type="text" id="first-name" name="first-name" required />
            <label htmlFor="last-name">Last Name:</label>
            <input type="text" id="last-name" name="last-name" required />
            <label htmlFor="communication-channel">Preferred Communication Channel:</label>
            <select id="communication-channel" name="communication-channel" required>
              <option value="">Select</option>
              <option value="in-app">In-app Messaging</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push Notifications</option>
            </select>
            <label htmlFor="age-range">Age Range:</label>
            <select id="age-range" name="age-range" required>
              <option value="">Select</option>
              <option value="under-18">Under 18</option>
              <option value="18-24">18-24</option>
              <option value="25-34">25-34</option>
              <option value="35-44">35-44</option>
              <option value="45-54">45-54</option>
              <option value="55-64">55-64</option>
              <option value="65+">65+</option>
            </select>
            <label htmlFor="location">Location:</label>
            <input type="text" id="location" name="location" required />
            <label htmlFor="education">Education Level:</label>
            <select id="education" name="education" required>
              <option value="">Select</option>
              <option value="high-school">High School</option>
              <option value="bachelors">Bachelor's Degree</option>
              <option value="masters">Master's Degree</option>
              <option value="doctorate">Doctorate</option>
              <option value="other">Other</option>
            </select>
            <label htmlFor="employment">Employment Status:</label>
            <select id="employment" name="employment" required>
              <option value="">Select</option>
              <option value="student">Student</option>
              <option value="employed">Employed</option>
              <option value="self-employed">Self-employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="retired">Retired</option>
            </select>
            <label htmlFor="industry">Industry or Field of Work:</label>
            <input type="text" id="industry" name="industry" required />
            <label htmlFor="learning-goals">Learning Goals:</label>
            <textarea id="learning-goals" name="learning-goals" required></textarea>
            <button type="submit" className="cta-button">Send Invitation</button>
          </form>
        </div>
        <div className="questions" id="invited-section" style={{ display: 'none' }}>
          <h3>Invited User: Please review and confirm your information:</h3>
          <form id="invited-form">
            <label htmlFor="inv-first-name">First Name:</label>
            <input type="text" id="inv-first-name" name="inv-first-name" readOnly />
            <label htmlFor="inv-last-name">Last Name:</label>
            <input type="text" id="inv-last-name" name="inv-last-name" readOnly />
            <label htmlFor="inv-communication-channel">Preferred Communication Channel:</label>
            <select id="inv-communication-channel" name="inv-communication-channel" disabled>
              <option value="">Select</option>
              <option value="in-app">In-app Messaging</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push Notifications</option>
            </select>
            <label htmlFor="inv-age-range">Age Range:</label>
            <select id="inv-age-range" name="inv-age-range" disabled>
              <option value="">Select</option>
              <option value="under-18">Under 18</option>
              <option value="18-24">18-24</option>
              <option value="25-34">25-34</option>
              <option value="35-44">35-44</option>
              <option value="45-54">45-54</option>
              <option value="55-64">55-64</option>
              <option value="65+">65+</option>
            </select>
            <label htmlFor="inv-location">Location:</label>
            <input type="text" id="inv-location" name="inv-location" readOnly />
            <label htmlFor="inv-education">Education Level:</label>
            <select id="inv-education" name="inv-education" disabled>
              <option value="">Select</option>
              <option value="high-school">High School</option>
              <option value="bachelors">Bachelor's Degree</option>
              <option value="masters">Master's Degree</option>
              <option value="doctorate">Doctorate</option>
              <option value="other">Other</option>
            </select>
            <label htmlFor="inv-employment">Employment Status:</label>
            <select id="inv-employment" name="inv-employment" disabled>
              <option value="">Select</option>
              <option value="student">Student</option>
              <option value="employed">Employed</option>
              <option value="self-employed">Self-employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="retired">Retired</option>
            </select>
            <label htmlFor="inv-industry">Industry or Field of Work:</label>
            <input type="text" id="inv-industry" name="inv-industry" readOnly />
            <label htmlFor="inv-learning-goals">Learning Goals:</label>
            <textarea id="inv-learning-goals" name="inv-learning-goals" readOnly></textarea>
            <button type="submit" className="cta-button">Confirm and Join</button>
          </form>
        </div>
      </main>
      <footer>
        <p>Connect with us on social media:</p>
        <nav>
          <a href="https://twitter.com/agu">Twitter</a>
          <a href="https://facebook.com/agu">Facebook</a>
          <a href="https://instagram.com/agu">Instagram</a>
        </nav>
        <p>&copy; 2023 Aspire, Grow, Unite. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default InvitationForm;
