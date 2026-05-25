# Review Widget Design Reference

The review widget is a single-page interface presented via `show_widget`. It lets the team member review, edit, and copy all five post-call deliverables before taking action in any external tool. Nothing is executed automatically.

**Design principles:**
- One widget, five tabs — no sequential questions
- Every field is editable inline
- Copy button per section — copies the full content to clipboard
- Feels like a product, not a form

---

## Design System

```
Colors:
  Primary:     #1B3A5C  (dark navy)
  Accent:      #00C4CC  (teal)
  Background:  #F0F4F8
  Card bg:     #FFFFFF
  Risk-green:  #D4EDDA / #28A745
  Risk-yellow: #FFF3CD / #856404
  Risk-red:    #F8D7DA / #DC3545
  Text:        #1A1A2E
  Muted:       #6C757D

Typography:
  Font: system-ui, -apple-system, sans-serif
  Heading: 600 weight
  Body: 400 weight, 14px

Spacing: 8px grid
Border radius: 8px cards, 4px inputs
Shadows: 0 2px 8px rgba(0,0,0,0.08)
```

---

## Widget Structure

```
┌─────────────────────────────────────────────────────────┐
│  HEADER: Customer name · Call type · Call date          │
├─────────────────────────────────────────────────────────┤
│  TAB BAR: Email │ Time Entry │ Slack Card │ Slack Post │ Action Items │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ACTIVE TAB CONTENT                                     │
│  ┌───────────────────────────────────────────────┐     │
│  │  Section label + helper text                  │     │
│  │  ┌─────────────────────────────────────────┐  │     │
│  │  │  editable textarea (pre-populated)      │  │     │
│  │  └─────────────────────────────────────────┘  │     │
│  │  [📋 Copy to Clipboard]                        │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  FOOTER: Destination reminder per active tab            │
└─────────────────────────────────────────────────────────┘
```

---

## Full HTML Template

Use this as the basis for `show_widget`. Replace all [PLACEHOLDER] values with extracted content before rendering.

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #F0F4F8; color: #1A1A2E; font-size: 14px; }

  .header {
    background: linear-gradient(135deg, #1B3A5C, #0F2540);
    color: white; padding: 20px 24px; border-radius: 12px 12px 0 0;
  }
  .header h2 { font-size: 18px; font-weight: 600; }
  .header .meta { font-size: 12px; opacity: 0.75; margin-top: 4px; }

  .tab-bar {
    background: white; border-bottom: 2px solid #E2E8F0;
    display: flex; padding: 0 16px; gap: 4px; overflow-x: auto;
  }
  .tab {
    padding: 12px 16px; cursor: pointer; font-size: 13px; font-weight: 500;
    color: #6C757D; border-bottom: 3px solid transparent; margin-bottom: -2px;
    white-space: nowrap; transition: all 0.15s; background: none; border-top: none;
    border-left: none; border-right: none;
  }
  .tab.active { color: #1B3A5C; border-bottom-color: #00C4CC; }

  .tab-content { display: none; padding: 20px; }
  .tab-content.active { display: block; }

  .section-label {
    font-size: 12px; font-weight: 600; color: #6C757D;
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
  }
  .helper-text {
    font-size: 12px; color: #6C757D; margin-bottom: 10px; line-height: 1.5;
  }

  .editable {
    width: 100%; border: 1px solid #E2E8F0; border-radius: 8px;
    padding: 14px; font-size: 13px; line-height: 1.7; color: #1A1A2E;
    resize: vertical; min-height: 200px; font-family: inherit;
    background: white; transition: border-color 0.15s;
  }
  .editable:focus { outline: none; border-color: #00C4CC; }

  .copy-btn {
    margin-top: 10px; padding: 8px 18px;
    background: #1B3A5C; color: white; border: none;
    border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; transition: opacity 0.15s;
    display: inline-flex; align-items: center; gap: 6px;
  }
  .copy-btn:hover { opacity: 0.85; }
  .copy-btn.copied { background: #28A745; }

  .risk-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 12px; font-weight: 600; margin-bottom: 10px;
  }
  .risk-positive { background: #D4EDDA; color: #155724; }
  .risk-neutral   { background: #E2E8F0; color: #4A5568; }
  .risk-atrisk    { background: #F8D7DA; color: #721C24; }

  .confidence-note {
    font-size: 11px; color: #856404; background: #FFF3CD;
    border-radius: 6px; padding: 6px 10px; margin-bottom: 12px;
    display: none;
  }
  .confidence-note.visible { display: block; }

  .action-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .action-table th {
    text-align: left; padding: 8px 10px; background: #F0F4F8;
    font-weight: 600; color: #4A5568; border-bottom: 2px solid #E2E8F0;
  }
  .action-table td {
    padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: top;
  }
  .action-table td input {
    width: 100%; border: 1px solid #E2E8F0; border-radius: 4px;
    padding: 4px 6px; font-size: 12px; font-family: inherit;
  }
  .action-table td input:focus { outline: none; border-color: #00C4CC; }
  .action-table tr:hover td { background: #F8FAFC; }

  .footer {
    background: white; border-top: 1px solid #E2E8F0;
    padding: 12px 20px; border-radius: 0 0 12px 12px;
    font-size: 12px; color: #6C757D;
  }
  .footer span { font-weight: 500; color: #1B3A5C; }
</style>

<div class="header">
  <h2>[CUSTOMER_NAME]</h2>
  <div class="meta">[CALL_TYPE] &nbsp;·&nbsp; [CALL_DATE] &nbsp;·&nbsp; [PARTICIPANT_COUNT] attendees</div>
</div>

<div class="tab-bar">
  <button class="tab active" onclick="showTab('email', this)">✉️ Email</button>
  <button class="tab" onclick="showTab('time-entry', this)">⏱ Time Entry</button>
  <button class="tab" onclick="showTab('slack-card', this)">📋 Slack Card</button>
  <button class="tab" onclick="showTab('slack-post', this)">💬 Slack Post</button>
  <button class="tab" onclick="showTab('action-items', this)">✅ Action Items</button>
</div>

<!-- EMAIL TAB -->
<div id="tab-email" class="tab-content active">
  <div class="section-label">Gmail Recap Draft</div>
  <div class="helper-text">Review and edit, then copy and paste into Gmail. Attach any decks from Google Drive before sending.</div>
  <div style="margin-bottom:8px; font-size:12px; color:#4A5568;">
    <strong>To:</strong> [ATTENDEE_EMAILS]<br>
    <strong>Subject:</strong> [EMAIL_SUBJECT]
  </div>
  <textarea class="editable" id="email-body" style="min-height:320px">[EMAIL_BODY]</textarea>
  <button class="copy-btn" onclick="copySection('email-body', this)">📋 Copy Email</button>
</div>

<!-- TIME ENTRY TAB -->
<div id="tab-time-entry" class="tab-content">
  <div class="section-label">Time Entry Notes</div>
  <div class="helper-text">Paste this into the Notes field of your time-tracking tool. Fill in the duration manually.</div>
  <textarea class="editable" id="time-entry-notes" style="min-height:100px">[TIME_ENTRY_NOTES]</textarea>
  <button class="copy-btn" onclick="copySection('time-entry-notes', this)">📋 Copy Notes</button>
</div>

<!-- SLACK CARD TAB -->
<div id="tab-slack-card" class="tab-content">
  <div class="section-label">Slack List Card Update</div>
  <div class="helper-text">Paste this into your project card on the Slack List. Adjust before posting if anything looks off.</div>

  <div id="confidence-flag" class="confidence-note [CONFIDENCE_VISIBLE]">
    ⚠️ [CONFIDENCE_NOTE]
  </div>
  <textarea class="editable" id="slack-card-body" style="min-height:200px">[SLACK_CARD_BODY]</textarea>
  <button class="copy-btn" onclick="copySection('slack-card-body', this)">📋 Copy Card Update</button>
</div>

<!-- SLACK POST TAB -->
<div id="tab-slack-post" class="tab-content">
  <div class="section-label">Internal Slack Action Items</div>
  <div class="helper-text">Paste this into the customer's Slack channel to tag internal team members on their action items.</div>
  <textarea class="editable" id="slack-post-body" style="min-height:180px">[SLACK_POST_BODY]</textarea>
  <button class="copy-btn" onclick="copySection('slack-post-body', this)">📋 Copy Slack Post</button>
</div>

<!-- ACTION ITEMS TAB -->
<div id="tab-action-items" class="tab-content">
  <div class="section-label">Full Action Item List</div>
  <div class="helper-text">All action items from the call — internal and customer-facing. Edit inline, then copy as text or share directly.</div>
  <table class="action-table" id="action-table">
    <thead>
      <tr>
        <th style="width:40%">Action</th>
        <th style="width:20%">Owner</th>
        <th style="width:15%">Due Date</th>
        <th style="width:25%">Notes</th>
      </tr>
    </thead>
    <tbody id="action-rows">
      <!-- Rows injected by JS from ACTION_ITEMS_JSON -->
    </tbody>
  </table>
  <button class="copy-btn" onclick="copyTable(this)" style="margin-top:12px">📋 Copy as Text</button>
</div>

<div class="footer" id="tab-footer">
  → Paste email into <span>Gmail</span> &nbsp;·&nbsp; time entry notes into <span>your time-tracking tool</span> &nbsp;·&nbsp; Slack card into <span>your project card</span> &nbsp;·&nbsp; Slack post into <span>customer channel</span>
</div>

<script>
  function showTab(name, el) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    el.classList.add('active');
  }

  function copySection(id, btn) {
    const val = document.getElementById(id).value;
    navigator.clipboard.writeText(val).then(() => {
      const orig = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = orig; btn.classList.remove('copied'); }, 2000);
    });
  }

  function copyTable(btn) {
    const rows = document.querySelectorAll('#action-rows tr');
    let text = 'Action\tOwner\tDue Date\tNotes\n';
    rows.forEach(row => {
      const cells = row.querySelectorAll('input');
      text += Array.from(cells).map(c => c.value).join('\t') + '\n';
    });
    navigator.clipboard.writeText(text).then(() => {
      const orig = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = orig; btn.classList.remove('copied'); }, 2000);
    });
  }

  // Inject action items rows from JSON
  const ACTION_ITEMS = [ACTION_ITEMS_JSON];
  const tbody = document.getElementById('action-rows');
  ACTION_ITEMS.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input value="${escHtml(item.action)}"></td>
      <td><input value="${escHtml(item.owner)}"></td>
      <td><input value="${escHtml(item.due_date || '')}"></td>
      <td><input value="${escHtml(item.notes || '')}"></td>
    `;
    tbody.appendChild(tr);
  });

  function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
</script>
```

---

## How to Populate the Template

Replace all `[PLACEHOLDER]` values before calling `show_widget`.

| Placeholder | Value |
|-------------|-------|
| `[CUSTOMER_NAME]` | e.g., "<Account>" |
| `[CALL_TYPE]` | e.g., "Onboarding Kickoff" |
| `[CALL_DATE]` | e.g., "May 20, 2026" |
| `[PARTICIPANT_COUNT]` | e.g., "4" |
| `[ATTENDEE_EMAILS]` | Comma-separated customer emails from Google Calendar |
| `[EMAIL_SUBJECT]` | Full subject line |
| `[EMAIL_BODY]` | Full plain-text email body (not HTML) |
| `[TIME_ENTRY_NOTES]` | 2-3 sentence shorthand |
| `[CONFIDENCE_VISIBLE]` | `visible` if there is a conflict to flag; otherwise empty |
| `[CONFIDENCE_NOTE]` | e.g., "Transcript suggests positive, but recent Slack messages flag a blocker — confirm before posting." |
| `[SLACK_CARD_BODY]` | Full formatted card update text |
| `[SLACK_POST_BODY]` | Full formatted internal Slack post |
| `[ACTION_ITEMS_JSON]` | JS array: `[{action, owner, due_date, notes}, ...]` |

---

## Slack Card Body Format

Pre-populate the slack-card-body textarea with this structure:

```
MM/DD -
Risk: [High / Medium / Low]
Trend: [Improving / Stable / Declining]
[Narrative update in first person — what happened, where the project stands, what is next. 2-4 sentences, plain prose.]

Path to green: [Medium/High risk only — narrative paragraph, mentions owner and exec sponsor naturally in the prose. Omit entirely for Low risk.]
```

---

## Notes

- The Email tab textarea uses plain text. The team member sends directly from Gmail — no HTML rendering needed in the widget.
- The Action Items tab uses an editable table with text inputs per cell. The "Copy as Text" button exports tab-separated values for easy pasting into any spreadsheet or project tool.
- If the recording link was not found, pre-fill the email body with [INSERT RECORDING LINK] and [INSERT PASSCODE] so it is obvious to the team member before they send.
