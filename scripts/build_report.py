#!/usr/bin/env python3
"""Build the report from the recorded evidence. Requires reportlab and matplotlib."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
for name, filename in [('ReportSans','DejaVuSans.ttf'),('ReportSans-Bold','DejaVuSans-Bold.ttf'),('ReportMono','DejaVuSansMono.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/filename)))
pdfmetrics.registerFontFamily('ReportSans',normal='ReportSans',bold='ReportSans-Bold',italic='ReportSans',boldItalic='ReportSans-Bold')
E=ROOT/'evidence/run-20261125'
S=json.loads((E/'summary.json').read_text())
OUT=ROOT/'docs'
GREEN='#235d49'; INK='#142c26'; MUTED='#58665f'; LIGHT='#edf3ef'; AMBER='#a66b26'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,ax=plt.subplots(figsize=(8,3.1),dpi=180)
labels=['Baseline\n6 candidates','Expanded patterns\n10 candidates','Positive control*\n11 candidates']
values=[x['recovered'] for x in S['stages']]
bars=ax.barh(labels,values,color=[GREEN,GREEN,AMBER],height=.48)
ax.invert_yaxis(); ax.set_xlim(0,6.9); ax.set_xticks(range(7)); ax.set_xlabel('Fictional accounts recovered (out of 6)',labelpad=9)
for b,v in zip(bars,values):ax.text(v+.1,b.get_y()+b.get_height()/2,f'{v}/6',va='center',fontweight='bold',color=INK)
for side in ('top','right','left'):ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color('#ccd8cf'); ax.tick_params(axis='y',length=0,pad=10)
ax.xaxis.grid(True,color='#e1e8e3'); ax.set_axisbelow(True)
fig.tight_layout();fig.savefig(OUT/'results.png',bbox_inches='tight',facecolor='white');plt.close(fig)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='ReportSans-Bold',fontSize=32,leading=37,textColor=colors.HexColor(INK),spaceAfter=16))
styles.add(ParagraphStyle(name='H1X',fontName='ReportSans-Bold',fontSize=22,leading=27,textColor=colors.HexColor(INK),spaceAfter=15))
styles.add(ParagraphStyle(name='H2X',fontName='ReportSans-Bold',fontSize=13,leading=18,textColor=colors.HexColor(GREEN),spaceBefore=16,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyX',fontName='ReportSans',fontSize=10.2,leading=15,textColor=colors.HexColor(INK),spaceAfter=9))
styles.add(ParagraphStyle(name='SmallX',fontName='ReportSans',fontSize=8.5,leading=12,textColor=colors.HexColor(MUTED),spaceAfter=7))
styles.add(ParagraphStyle(name='LabelX',fontName='ReportSans-Bold',fontSize=9,leading=13,textColor=colors.HexColor(GREEN),spaceAfter=12))
styles.add(ParagraphStyle(name='CellX',fontName='ReportSans',fontSize=9,leading=12,textColor=colors.HexColor(INK)))
styles.add(ParagraphStyle(name='CodeX',fontName='ReportMono',fontSize=8.2,leading=12,textColor=colors.HexColor(INK),spaceAfter=7))
W=A4[0]-96
story=[]
def p(text,kind='BodyX'):return Paragraph(text,styles[kind])
def add(text,kind='BodyX'):story.append(p(text,kind))
def heading(t):add(t,'H2X')
def table(rows,widths):
 t=Table([[p(escape(str(c)),'CellX') for c in row] for row in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(LIGHT)),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#c9d8cc')),('LINEBELOW',(0,1),(-1,-1),.4,colors.HexColor('#dce3dd')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
 story.append(t);story.append(Spacer(1,10))
def page(label,title):
 if story:story.append(PageBreak())
 add(label.upper(),'LabelX');add(title,'H1X')

add('INDEPENDENT SECURITY REPORT  /  25 NOVEMBER 2026','LabelX')
add('Password Exposure<br/>&amp; Defense','TitleX')
add('A controlled offline password-auditing lab','H1X')
add('Mustafa Al Azzawi','H2X')
add('Reproducible experiment. Fictional credentials. Measured results.','SmallX')
story.append(Spacer(1,17))
heading('Executive summary')
add('What can a small dictionary test establish after a readable password-hash copy is available? This lab creates six fictional accounts and compares three deliberately constructed candidate lists using John the Ripper core 1.9.0. Each run starts with an empty recovery cache.')
table([['BASELINE','EXPANDED PATTERNS','POSITIVE CONTROL'],['3 of 6 recovered','5 of 6 recovered','6 of 6 recovered'],['6 candidates','10 candidates','11 candidates; known random plaintext included']], [W/3]*3)
add('<b>The key result:</b> changing the candidates changes the outcome. Failure to find a password in a short list does not prove it is secure. The control run deliberately includes the final password; it is not a successful guess of an unknown random secret.')
heading('What this report establishes')
add('The raw logs support the recovery counts above. The runner passed 23 fixture/result assertions; a separate verifier checked the recorded output, wordlist coverage, checksums, and summary. No device intrusion, real account test, malware, or network login was performed.')
add('This is a new experiment executed on 25 November 2026, not a reconstruction of undocumented historical results. Preparation and tool provenance are described on page 5.','SmallX')

page('Experiment design','A deliberately bounded test')
heading('Question and starting assumption')
add('How does candidate-list content affect recovery of salted password hashes? The test begins with readable synthetic hashes. Obtaining those hashes, gaining physical access, and using any recovered credential are outside the experiment.')
table([['FIXTURE','PUBLIC TEACHING PASSWORD / PATTERN'],['lab_numeric','123456'],['lab_dictionary','password'],['lab_season','Summer2026!'],['lab_context','Orion1998! (fictional context)'],['lab_reuse','password, with a different salt'],['lab_random','24 characters generated with Python secrets; recorded in fixtures.json']], [135,W-135])
heading('Fixed configuration')
add('Linux x86_64; Python 3; OpenSSL 3.5.9; John core 1.9.0. Hashes use SHA-512-crypt ($6$), OpenSSL\'s default 5,000 rounds, and six unique fixture salts. This is a compatibility-focused teaching configuration, not a recommendation for new production storage.')
heading('Controlled comparison')
add('The baseline contains six candidates. The expanded list adds four season/name/year patterns. The positive control adds the generated random plaintext. The same six hashes are used in all runs, with no rules or brute-force mode. Fresh local pot files prevent previously recovered values from contaminating the comparison [1].')
add('Equal plaintexts produce different stored hashes in this fixture because their salts differ. Every recovered plaintext is compared with the fixture manifest. Outputs include command lines, stdout, stderr, --show results, and SHA-256 input digests.')

page('Measured evidence','Results, with their limits')
story.append(Image(str(OUT/'results.png'),width=W,height=W*3.1/8))
add('* Positive control deliberately includes the known random plaintext. This is a fixture-validation run, not a strength test.','SmallX')
rows=[['ACCOUNT','BASELINE','EXPANDED','CONTROL']]
for f in json.loads((E/'fixtures.json').read_text()):
 rows.append([f['account']]+['Recovered' if f['account'] in r['accounts'] else 'Not found' for r in S['stages']])
table(rows,[W*.28,W*.24,W*.24,W*.24])
heading('Interpretation')
add('The first list contains passwords matching three accounts; the second adds matches for two more. Uppercase letters, a year, and punctuation did not stop recovery when those exact patterns were in the list. The random example was absent until the control deliberately supplied it.')
heading('What cannot be concluded')
add('These are constructed examples, not a representative password sample. No exhaustive search, time-to-crack estimate, population crack rate, hardware comparison, or production security claim follows. John\'s displayed speeds are incidental. A different list could recover a password missed by these lists.')

page('Defensive interpretation','Protect exposure and authentication separately')
add('The experiment verifies candidates against an already readable hash copy. A real defense needs to address several different boundaries; this lab did not test the controls below.')
table([['BOUNDARY','REVIEW ACTION','LIMIT'],['Hash exposure','Restrict hash and backup access; review storage design.','Physical possession alone does not prove readable hashes.'],['Offline guessing','Use unique generated passwords and suitable costly salted hashing [2].','Salts do not stop checking a known candidate.'],['Online authentication','Review MFA and online rate limits [2].','These do not block offline comparisons against a copied hash.'],['Device data','Review disk encryption and protected recovery handling [3].','An unlocked or compromised session is a different risk.'],['Removable media','Follow approved-media handling; do not connect found devices [4].','This lab did not test USB execution or device policy.']], [100,218,W-318])
heading('Practical follow-up')
add('For a real authorized assessment, collect configuration evidence and a defined test plan for each boundary. Record what was observed, what was tested, and what remains unknown. Never present a recommended control as implemented or effective without checking it.')
heading('Common misconceptions corrected')
add('<b>Hashing is not decryption.</b> A candidate is processed and compared with the stored verifier.<br/><b>Not recovered is not proven safe.</b> It only describes the selected candidates.<br/><b>A console warning is not proof of compromise.</b> A claim of data theft or remote access needs execution and network evidence.<br/><b>Physical access is conditional risk.</b> Encryption, device state, permissions, and key protection matter.')

page('Reproduction & provenance','Evidence you can inspect and repeat')
add('The companion source ZIP includes the runner, an independent evidence verifier, setup script, report source, and Arabic interview notes. Existing evidence is never overwritten by the runner.')
for line in ['bash scripts/setup-john.sh','python3 run_lab.py --john-dir tools/john-1.9.0/run \\','  --output evidence/my-new-run','python3 verify_evidence.py evidence/my-new-run']:add(escape(line),'CodeX')
add('The setup is tested for Linux x86_64 and requires Python 3, OpenSSL, a C compiler, make, curl, and tar/xz. Internet is used only to obtain the official dependency. The experiment is local. A fresh run generates a new random comparison; recovery counts should remain 3, 5, and 6.','SmallX')
heading('Recorded execution')
add(f"UTC timestamp: {escape(S['executed_at_utc'])}<br/>Tool: {escape(S['john'])}<br/>Input digest: <font face='ReportMono' size='7'>{S['fixture_sha256']}</font>",'SmallX')
heading('Preparation and ownership')
add('Independent report prepared for Mustafa Al Azzawi with Codex assistance. New scripts, experiments, and analysis were produced in the assistant\'s Linux environment under his direction. Earlier presentation files are not republished. Mustafa should reproduce and understand the lab before using the new implementation as an interview demonstration.','SmallX')
heading('References')
refs=[('1','Openwall - command options and wordlist mode','https://www.openwall.com/john/doc/OPTIONS.shtml'),('','Wordlist-mode documentation','https://www.openwall.com/john/doc/MODES.shtml'),('2','NIST SP 800-63B-4 - Password Verifiers; Appendix A','https://pages.nist.gov/800-63-4/sp800-63b.html'),('3','Apple Platform Security - FileVault volume encryption','https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/1/web/1'),('4','CISA - Risks of Using Portable Devices','https://www.cisa.gov/sites/default/files/publications/RisksOfPortableDevices.pdf')]
for n,t,u in refs:add(f"{'['+n+'] ' if n else ''}<a href='{u}' color='{GREEN}'>{escape(t)}</a>",'SmallX')
add('Sources checked 25 November 2026. Educational report; no compliance certification. John is an external dependency under its own license; no binary is bundled.','SmallX')

def furniture(c,doc):
 c.saveState();c.setStrokeColor(colors.HexColor('#dce3dd'));c.setLineWidth(.6)
 c.line(48,A4[1]-35,A4[0]-48,A4[1]-35)
 c.setFont('ReportSans-Bold',8);c.setFillColor(colors.HexColor(GREEN));c.drawString(48,A4[1]-25,'MA  /  SECURITY LAB')
 c.setFont('ReportSans',8);c.setFillColor(colors.HexColor(MUTED));c.drawRightString(A4[0]-48,A4[1]-25,'Independent educational report')
 c.line(48,37,A4[0]-48,37);c.drawString(48,24,'Mustafa Al Azzawi  |  November 2026');c.drawRightString(A4[0]-48,24,str(doc.page));c.restoreState()
SimpleDocTemplate(str(OUT/'Password-Security-Report.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=53,bottomMargin=53,title='Password Exposure & Defense',author='Mustafa Al Azzawi').build(story,onFirstPage=furniture,onLaterPages=furniture)
print(OUT/'Password-Security-Report.pdf')
