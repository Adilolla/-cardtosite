<div align="center">
  <h1>CardToSite</h1>
  <h3>AI-Powered Business Card → Website Generator</h3>
</div>

<hr/>

<h2>Overview</h2>
<p>
  CardToSite converts any business card image into a clean, responsive website with zero manual input.
  Using Google’s Gemini 2.5 Flash model, it extracts key details, detects brand colors, and generates a complete HTML page automatically.
</p>

<hr/>

<h2>What CardToSite Does</h2>
<ul>
  <li>Extracts key details: Name, Title, Company, Email, Phone, Website, Address</li>
  <li>Detects primary brand colors from the business card</li>
  <li>Generates a fully responsive HTML/CSS webpage</li>
  <li>Provides a CLI tool and lightweight REST API</li>
  <li>Requires nothing from the user except uploading a business card image</li>
</ul>

<hr/>

<h2>How It Works</h2>
<ol>
  <li>User uploads a business card image</li>
  <li>The image is processed by the Gemini 2.5 Flash model</li>
  <li>The model outputs structured JSON with detected information</li>
  <li>A Python template renders the data into a clean HTML page</li>
  <li>The output is saved locally or returned via API</li>
</ol>

<hr/>

<h2>Requirements</h2>
<ul>
  <li>Python 3.9+</li>
  <li>Gemini 2.5 Flash API key</li>
</ul>

<hr/>

<h2>Tech Stack</h2>
<ul>
  <li><strong>Backend:</strong> Python, Flask</li>
  <li><strong>AI:</strong> Gemini 2.5 Flash</li>
  <li><strong>Database (optional):</strong> PostgreSQL or SQLite</li>
  <li><strong>Output:</strong> Responsive HTML/CSS</li>
</ul>

<hr/>

<h2>Project Vision</h2>
<p>
  CardToSite aims to simplify the process of transforming a physical business card into an instant online identity.
  The MVP focuses on accuracy, clean design, and minimal user friction, enabling fast digital onboarding for freelancers,
  entrepreneurs, and small businesses.
</p>

<hr/>

<h2>Future Enhancements (Beyond MVP)</h2>
<ul>
  <li>Multiple design themes</li>
  <li>Editable fields before export</li>
  <li>QR code integration</li>
  <li>Automated hosting and deployment</li>
  <li>User accounts and saved websites</li>
</ul>

<hr/>

<div align="center">
  <i>“Your business card becomes a website — instantly.”</i>
</div>
