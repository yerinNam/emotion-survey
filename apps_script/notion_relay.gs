/**
 * Notion relay for the emotion survey (Google Apps Script web app).
 *
 * The survey page POSTs the participant's JSONL here on submit; this script
 * creates one child page per participant under the Notion page for that
 * language, with the JSONL in a code block.
 *
 * Setup
 *  1. script.google.com → New project → paste this file.
 *  2. Project Settings → Script properties → add NOTION_TOKEN = <Notion integration secret>.
 *     (Never put the token in this file or in the survey HTML.)
 *  3. In Notion, add the integration to both pages (⋯ → Connections).
 *  4. Deploy → New deployment → Web app; Execute as: Me; Who has access: Anyone.
 *  5. Put the /exec URL in CONFIG.notionUrl of src/survey_template.html (both versions) and rebuild.
 */

const NOTION_PAGES = {
  ko: '421528c8923c80bea610d28d0eb46c8f',   // 인지와 정서 - 데이터 수집 (ko)
  en: '421528c8923c80b497eefce86a086387'    // 인지와 정서 - 데이터 수집 (en)
};
const NOTION_VERSION = '2022-06-28';
const CHUNK = 2000;          // Notion limit: characters per rich_text item
const ITEMS_PER_BLOCK = 100; // Notion limit: rich_text items per block
const MAX_TEXT = 1500000;    // reject absurdly large bodies

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    const parent = NOTION_PAGES[d.lang];
    if (!parent) throw new Error('unknown lang');
    const name = String(d.name || '');
    if (!/^emotion_survey_[\w.\-가-힣]+\.jsonl$/.test(name)) throw new Error('bad file name');
    const text = String(d.text || '');
    if (!text || text.length > MAX_TEXT) throw new Error('bad text size');
    // Every line must be a JSON object from this survey
    const lines = text.split('\n').filter(Boolean).map(l => JSON.parse(l));
    if (!lines.length || !lines.every(l => l && l.participant_id !== undefined && l.part)) throw new Error('not survey JSONL');

    const first = lines[0];
    const info = `participant_id: ${first.participant_id} · session_id: ${first.session_id} · lines: ${lines.length} · received: ${new Date().toISOString()}`;
    const children = [{ object: 'block', type: 'paragraph', paragraph: { rich_text: [{ type: 'text', text: { content: info } }] } }]
      .concat(codeBlocks(text));

    const res = notion('post', '/v1/pages', {
      parent: { page_id: parent },
      properties: { title: { title: [{ type: 'text', text: { content: name } }] } },
      children: children.slice(0, 100)
    });
    // Notion accepts at most 100 children per request; append the rest if any
    for (let i = 100; i < children.length; i += 100) {
      notion('patch', `/v1/blocks/${res.id}/children`, { children: children.slice(i, i + 100) });
    }
    return json({ ok: true, page: res.url });
  } catch (err) {
    console.error(err);
    return json({ ok: false, error: String(err && err.message || err) });
  }
}

// Whole JSONL in as few code blocks as possible (copy → paste into a .jsonl file)
function codeBlocks(text) {
  const pieces = [];
  for (let i = 0; i < text.length; i += CHUNK) pieces.push({ type: 'text', text: { content: text.slice(i, i + CHUNK) } });
  const blocks = [];
  for (let i = 0; i < pieces.length; i += ITEMS_PER_BLOCK) {
    blocks.push({ object: 'block', type: 'code', code: { language: 'json', rich_text: pieces.slice(i, i + ITEMS_PER_BLOCK) } });
  }
  return blocks;
}

function notion(method, path, body) {
  const token = PropertiesService.getScriptProperties().getProperty('NOTION_TOKEN');
  if (!token) throw new Error('NOTION_TOKEN script property is not set');
  const r = UrlFetchApp.fetch('https://api.notion.com' + path, {
    method: method,
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token, 'Notion-Version': NOTION_VERSION },
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });
  const out = JSON.parse(r.getContentText());
  if (r.getResponseCode() >= 300) throw new Error(`Notion ${r.getResponseCode()}: ${out.message}`);
  return out;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
