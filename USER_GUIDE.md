# License Uploader - User Guide

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Uploading Documents](#uploading-documents)
- [Reviewing Extracted License Terms](#reviewing-extracted-license-terms)
- [Refining Terms](#refining-terms)
- [Submitting to Alma](#submitting-to-alma)
- [Custom Prompt Customization](#custom-prompt-customization)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [FAQ](#faq)

---

## Introduction

The License Uploader is an AI-powered web application that streamlines the process of extracting license terms from vendor license documents and uploading them to Ex Libris Alma. Instead of manually reading through lengthy license agreements and entering terms one by one, the License Uploader uses Large Language Models (LLMs) to automatically extract 76+ license terms conforming to Digital Library Federation (DLF) standards.

### Key Benefits

- **Time Savings**: Reduce license processing time from hours to minutes
- **Accuracy**: AI-powered extraction minimizes human error
- **Standardization**: All terms conform to DLF/ERMI standards
- **Convenience**: Web-based interface accessible from any device
- **Flexibility**: Review and edit all extracted terms before submission

### Supported File Formats

- **PDF** (.pdf) - Most common format for license documents
- **Microsoft Word** (.docx) - Modern Word documents (Office 2007+)
- **Plain Text** (.txt) - Text files with UTF-8 encoding

**Note**: Legacy .doc files (Office 97-2003) are not supported. Please convert to .docx format using Microsoft Word or LibreOffice.

**File Size Limit**: 16 MB maximum

---

## Getting Started

### Accessing the Application

1. Open your web browser (Chrome, Firefox, Safari, or Edge recommended)
2. Navigate to the License Uploader URL provided by your system administrator
   - Development: `http://localhost:5000`
   - Production: Your institution's deployment URL
3. You should see the home page with the upload interface

### Required Information

Before you begin, gather the following information:

**Required:**
- License document (PDF, DOCX, or TXT)
- Unique license code (e.g., "LIC-2026-001")
- License name (e.g., "SpringerLink 2026 License")

**Optional but Recommended:**
- Vendor/Licensor name
- License start date
- License end date
- Review status

---

## Uploading Documents

### Step-by-Step Upload Process

#### 1. Choose Your Document

**Method 1: Click to Browse**
1. Click the "Choose File" button
2. Navigate to your license document
3. Select the file and click "Open"

**Method 2: Drag and Drop**
1. Locate your license document in File Explorer (Windows) or Finder (Mac/Linux)
2. Drag the file directly onto the upload area
3. Release to upload

#### 2. Verify File Information

After selecting a file, you'll see:
- File name
- File size
- File type

**Check that:**
- The file name is correct
- The file size is under 16 MB
- The file format is PDF, DOCX, or TXT

#### 3. Process the Document

1. Click the "Process Document" button
2. Wait for processing to complete (typically 10-30 seconds)
3. You'll be automatically redirected to the review page

**During Processing:**
- The document text is extracted
- AI analyzes the content
- 76+ license terms are automatically extracted
- Results are prepared for your review

### Upload Errors and Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No file uploaded" | No file selected | Select a file before clicking Process |
| "No file selected" | Empty file input | Choose a valid document file |
| "Invalid file type" | Unsupported format | Use PDF, DOCX, or TXT only |
| "File too large" | File exceeds 16 MB | Compress PDF or split into sections |
| "Uploaded file is empty" | File has no content | Verify file is not corrupted |
| "No text content could be extracted" | File is scanned image or corrupted | Use OCR software or re-save document |
| "Invalid file type detected" | File extension doesn't match content | Save file in correct format |

### Tips for Best Results

**Document Quality:**
- Use text-based PDFs (not scanned images)
- Ensure document is complete and readable
- Remove any password protection
- Use documents with clear formatting

**File Preparation:**
- If document is very large, extract just the license sections
- For scanned documents, use OCR software first (Adobe Acrobat, ABBYY FineReader)
- Test with a short sample document first

---

## Reviewing Extracted License Terms

After processing, you'll see the review page with three main sections:

### 1. Basic Information (Required)

At the top of the page, fill in the basic license information:

#### License Code (Required)
- **Purpose**: Unique identifier for the license in Alma
- **Format**: Any alphanumeric string (e.g., "LIC-2026-SPRINGER-001")
- **Tips**: Use a consistent naming convention
  - Include year: LIC-2026-XXX
  - Include vendor: LIC-SPRINGER-2026
  - Use sequential numbers: 001, 002, 003

#### License Name (Required)
- **Purpose**: Human-readable name displayed in Alma
- **Format**: Descriptive text (max 255 characters)
- **Examples**:
  - "SpringerLink Electronic Journals 2026"
  - "JSTOR Arts & Sciences Collection License"
  - "ProQuest Dissertations & Theses Global"

#### License Type (Required)
Choose from:
- **LICENSE**: Standard license agreement (most common)
- **AMENDMENT**: Modification to existing license
- **ADDENDUM**: Additional terms added to license

#### License Status (Required)
Choose from:
- **ACTIVE**: License is currently in effect
- **DRAFT**: License is being negotiated
- **EXPIRED**: License period has ended
- **RETIRED**: License no longer in use

#### Review Status (Optional)
- **IN REVIEW**: Default status for new uploads
- **APPROVED**: License has been reviewed and approved
- **PENDING**: Waiting for additional review

#### Vendor/Licensor (Optional)
- Start typing vendor name
- Select from dropdown list of vendors in Alma
- Creates proper link in Alma system

#### Start Date and End Date (Optional)
- Click calendar icon to select dates
- Format: YYYY-MM-DD (e.g., 2026-01-01)
- End date must be after start date

### 2. Extracted License Terms

The main section shows all 76 license terms organized by category. Each term shows:

- **Term Name**: Human-readable name
- **Term Code**: Alma term code (e.g., ARCHIVE, FAIRUSE)
- **Description**: What the term means
- **Extracted Value**: What the AI found in the document
- **Refine Button** (⚡): Re-analyze just this term

#### Term Types

**YES/NO Terms**
- Binary indicators (Yes or No)
- Examples: Fair Use Clause, Confidentiality of Agreement
- **Values**: Yes, No, or blank (unknown)

**Permitted/Prohibited Terms**
- Rights-based permissions
- Examples: Archiving Right, Interlibrary Loan, Course Reserves
- **Values**:
  - Permitted (Explicit) - Explicitly allowed
  - Permitted (Interpreted) - Implied permission
  - Prohibited (Explicit) - Explicitly forbidden
  - Prohibited (Interpreted) - Implied prohibition
  - Silent - Not mentioned in license
  - Uninterpreted - Mentioned but unclear
  - Not Applicable - Doesn't apply

**Free Text Terms**
- Open-ended text fields
- Examples: Governing Law, Authorized User Definition, Concurrent User
- **Values**: Any text extracted from document

**Renewal Type**
- How license renews
- **Values**: Explicit, Automatic

**Unit of Measure**
- Time intervals for notice periods
- **Values**: Week, Calendar Day, Month, Business Day

#### Searching and Filtering Terms

**Search Bar**:
- Type any text to filter terms
- Searches term names, codes, and values
- Clear search to show all terms

**Filter Dropdown**:
- **All Terms**: Show everything
- **Extracted Only**: Show terms with values
- **Empty Only**: Show terms without values
- **Specific Categories**: Filter by term type

### 3. Document Truncation Warning

If you see a yellow warning banner at the top:

**What it means:**
- The document was longer than 15,000 characters
- Only the first 15,000 characters were analyzed
- Some terms in later sections may have been missed

**What to do:**
1. Review all extracted terms carefully
2. Read the original document for terms in later sections
3. Manually fill in any missing terms
4. Use the Refine button for specific terms you want to re-check

---

## Refining Terms

The AI extraction is not perfect. You can refine individual terms if the extraction was incorrect or incomplete.

### When to Refine a Term

- The extracted value seems incorrect
- The term was not extracted but you know it's in the document
- You want to verify the AI's interpretation
- The value is ambiguous

### How to Refine a Term

1. **Locate the term** you want to refine
2. **Click the lightning bolt button** (⚡) next to the term
3. **Wait for re-analysis** (5-10 seconds)
4. **Review the new value**
5. **Accept or manually edit** as needed

### Refine Process

**Behind the scenes:**
- The AI re-reads the entire document
- Focuses specifically on the selected term
- Provides a fresh extraction
- Updates the field automatically

**Note**: Refinement uses the same AI model, so results may be similar. If you're certain of the correct value, it's faster to manually edit the field.

### Manual Editing

You can manually edit any term:

1. **Click in the field** to activate editing
2. **Type or select** the correct value
3. **Tab or click away** to save changes

**For dropdown terms** (Permitted/Prohibited, Yes/No):
- Click the dropdown to see all valid options
- Select the appropriate value
- AI-extracted values are validated against allowed options

**For text terms**:
- Type freely in the text box
- Copy/paste from the original document if needed
- Maximum length: 255 characters (most fields)

---

## Submitting to Alma

Once you've reviewed and edited all terms, you're ready to submit to Alma.

### Pre-Submission Checklist

Before clicking Submit, verify:

- [ ] License Code is unique and follows your naming convention
- [ ] License Name is descriptive and accurate
- [ ] License Type is correct (LICENSE, AMENDMENT, or ADDENDUM)
- [ ] License Status is appropriate (ACTIVE, DRAFT, EXPIRED, RETIRED)
- [ ] Vendor is selected (if known)
- [ ] Start Date and End Date are correct (if applicable)
- [ ] All critical terms have been reviewed
- [ ] Any blank fields are intentionally blank (not missed extractions)

### Validation

1. **Click the "Validate" button** (optional but recommended)
2. **Review validation results**:
   - ✅ Green checkmarks indicate required fields are filled
   - ❌ Red X's indicate missing required fields
   - Fix any errors before submitting

### Submit Process

1. **Click "Submit to Alma"** button (bottom right)
2. **Confirm submission** in the popup dialog
   - Review license code and name
   - Click "Confirm" to proceed or "Cancel" to go back
3. **Wait for submission** (5-15 seconds)
4. **Success confirmation**:
   - Green success message appears
   - License code is displayed
   - You're redirected to the home page

### After Submission

**In Alma:**
1. Log in to Alma
2. Navigate to Acquisitions > Licenses
3. Search for your license code
4. Verify all terms were imported correctly
5. Complete any additional Alma-specific fields
6. Attach the original license document (if desired)

### Submission Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "License code is required" | Missing code | Fill in License Code field |
| "License name is required" | Missing name | Fill in License Name field |
| "End date must be after start date" | Invalid dates | Correct the date range |
| "Invalid date format" | Wrong format | Use YYYY-MM-DD format |
| "Error creating license" | Alma API error | Check API key and permissions |
| "Session expired or invalid" | Session timeout | Upload document again |

---

## Custom Prompt Customization

Advanced users can customize the AI extraction prompt to improve results for specific license types or institutions.

### Accessing Prompt Settings

1. **Click "Settings"** or "Advanced" (location varies by deployment)
2. **Navigate to "Prompt Customization"**
3. **View current prompt template**

### Understanding the Prompt Template

The prompt template contains placeholders:

- `{terms_description}` - Automatically filled with all 76 license term definitions
- `{document_text}` - Automatically filled with the uploaded document text
- `{truncation_note}` - Warning if document was truncated

**Do not remove these placeholders** - they are required.

### Customizing the Prompt

**Example use cases:**
- Emphasize specific terms important to your institution
- Add context about your institution's interpretation policies
- Include examples of how to handle ambiguous language
- Add instructions for vendor-specific terminology

**Example customization:**

```
Analyze the following license agreement and extract all relevant license terms.

IMPORTANT: Our institution interprets "walk-in users" as authorized users
for all permissions unless explicitly stated otherwise.

For Permitted/Prohibited terms, use "Permitted (Explicit)" only when the
license uses words like "permitted," "allowed," "may," or "authorized."

LICENSE TERMS TO EXTRACT:
{terms_description}

DOCUMENT TEXT:
{document_text}

OUTPUT FORMAT:
Return a JSON object where each key is a term code and the value is the
extracted information or null.

Return ONLY valid JSON, no additional text.
```

### Saving Custom Prompt

1. **Edit the prompt** in the text area
2. **Verify placeholders** are still present
3. **Click "Save Custom Prompt"**
4. **Test with a sample document**
5. **Iterate as needed**

### Resetting to Default

1. **Click "Reset to Default Prompt"**
2. **Confirm reset**
3. **Custom prompt is deleted**, default is restored

**Note**: Custom prompts are stored server-side and apply to all users of the instance.

---

## Troubleshooting Common Issues

### Upload Issues

**Problem**: "No text content could be extracted from the file"

**Causes**:
- Document is a scanned image PDF (not text-based)
- Document is corrupted
- Document is password-protected
- Document format is unsupported

**Solutions**:
1. **For scanned PDFs**: Use OCR software to convert to text-based PDF
   - Adobe Acrobat Pro: Tools > Enhance Scans > Recognize Text
   - Online tools: Adobe Online OCR, Smallpdf OCR
2. **For corrupted files**: Re-download or re-save the document
3. **For password-protected**: Remove password protection in PDF reader
4. **For .doc files**: Convert to .docx using Microsoft Word or LibreOffice

---

**Problem**: "File too large. Maximum size is 16MB"

**Solutions**:
1. **Compress PDF**:
   - Adobe Acrobat: Save As > Reduced Size PDF
   - Online tools: Smallpdf, iLovePDF
2. **Extract license sections only**: Remove exhibits, schedules, non-license content
3. **Convert to text**: Save as .txt file with just the license text

---

**Problem**: Upload button is disabled or grayed out

**Solutions**:
1. Select a file first
2. Ensure file is correct format (PDF, DOCX, TXT)
3. Check file size is under 16 MB
4. Refresh the page and try again

### Extraction Issues

**Problem**: AI extracted the wrong value for a term

**Solutions**:
1. **Use Refine button** (⚡) to re-extract just that term
2. **Manually edit** the field with the correct value
3. **Check original document** to verify the correct value
4. **Consider custom prompt** if errors are systematic

---

**Problem**: Many terms are blank (not extracted)

**Possible causes**:
- License doesn't mention those terms (common)
- Document was truncated (check for yellow warning)
- Document has poor formatting or is scanned image
- AI model couldn't interpret the language

**Solutions**:
1. **Review original document** to confirm terms are actually present
2. **Manually fill in** any terms you find
3. **Use Refine button** for specific terms
4. **Check document quality** - is it text-based and readable?

---

**Problem**: "AI service took too long to respond (timeout after 180 seconds)"

**Causes**:
- LLM service is overloaded
- Network connectivity issues
- Document is extremely complex

**Solutions**:
1. **Wait a few minutes** and try again
2. **Check internet connection**
3. **Try with a shorter document** to test
4. **Contact system administrator** if issue persists

### Submission Issues

**Problem**: "Error creating license" when submitting to Alma

**Causes**:
- Alma API key is invalid or expired
- API key doesn't have required permissions
- License code already exists in Alma
- Network connectivity to Alma

**Solutions**:
1. **Check API key** with system administrator
2. **Verify permissions**: Acquisitions read/write, Vendors read
3. **Use unique license code** - check Alma for duplicates
4. **Test Alma connection** using test connection feature (if available)

---

**Problem**: "Session expired or invalid. Please upload your document again"

**Causes**:
- Session timeout (after 1 hour of inactivity)
- Browser cookies disabled
- Server restart

**Solutions**:
1. **Upload document again** - data is lost
2. **Complete workflow within 1 hour**
3. **Enable browser cookies**
4. **Save extracted data** (copy/paste) if concerned about timeout

---

**Problem**: Validation errors before submission

**Solutions**:
1. **Fill in all required fields**:
   - License Code
   - License Name
   - License Type
   - License Status
2. **Verify date formats** (YYYY-MM-DD)
3. **Ensure end date is after start date**

### Browser Issues

**Problem**: Page doesn't load or looks broken

**Solutions**:
1. **Clear browser cache**: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. **Try different browser**: Chrome, Firefox, Safari, Edge
3. **Disable browser extensions** that might interfere
4. **Check JavaScript is enabled**

---

**Problem**: Buttons don't respond when clicked

**Solutions**:
1. **Wait for page to fully load**
2. **Check browser console** for errors (F12 key)
3. **Refresh the page**
4. **Try different browser**

---

## FAQ

### General Questions

**Q: How long does the extraction process take?**

A: Typically 10-30 seconds depending on document length and AI service response time. Very long documents (near 16 MB) may take up to 60 seconds.

---

**Q: Can I save my work and come back later?**

A: No, the application does not save progress. Once you upload and extract terms, you should complete the review and submission in the same session. Sessions expire after 1 hour of inactivity.

**Workaround**: Copy the extracted terms to a text file or document for reference if you need to stop midway.

---

**Q: How accurate is the AI extraction?**

A: Accuracy varies by document quality and term type:
- **Clear explicit terms**: 85-95% accurate
- **Ambiguous or interpreted terms**: 60-75% accurate
- **Complex legal language**: 50-70% accurate

**Always review and verify** extracted terms before submission. The AI is a time-saving tool, not a replacement for human review.

---

**Q: Can I upload multiple documents at once?**

A: No, the application processes one document at a time. For multiple licenses, complete each upload-review-submit workflow separately.

---

**Q: What happens to my uploaded document?**

A: The document file is:
1. Temporarily saved during processing
2. Text is extracted and analyzed
3. File is deleted immediately after processing
4. Only extracted text is retained in session (deleted after submission)

**Security**: Documents are not permanently stored. Text is only retained for the active session.

---

### License Terms Questions

**Q: What does "Silent" mean for Permitted/Prohibited terms?**

A: "Silent" means the license document does not mention this term at all. It's neither explicitly permitted nor prohibited. Your institution's policies will determine how to interpret silent terms.

---

**Q: What's the difference between "Permitted (Explicit)" and "Permitted (Interpreted)"?**

A:
- **Permitted (Explicit)**: License clearly states "permitted," "allowed," "may," or similar explicit permission language
- **Permitted (Interpreted)**: License doesn't explicitly use permission words, but the context or overall license suggests it's allowed

Example: If license says "licensee may archive content" = Explicit. If license is silent on archiving but grants "perpetual access rights" = Interpreted (archiving implied).

---

**Q: What are the 76 license terms?**

A: The terms conform to Digital Library Federation (DLF) Electronic Resource Management Initiative (ERMI) standards. Categories include:

- **Access Rights**: Remote access, walk-in users, concurrent users
- **Usage Rights**: Print copy, digital copy, scholarly sharing
- **ILL Rights**: Electronic, print/fax, secure transmission
- **Course Rights**: Course reserves, course packs (print/electronic)
- **Perpetual Rights**: Archiving, perpetual access
- **Terms & Conditions**: Governing law, indemnification, confidentiality
- **Administrative**: Renewal type, termination rights, notice periods

Full list available in the review interface.

---

**Q: Can I add custom license terms not in the standard 76?**

A: No, the application only supports the predefined 76 DLF/ERMI standard terms that are recognized by Alma. Custom terms would need to be added manually in Alma after license creation.

---

### Technical Questions

**Q: What file formats are supported?**

A:
- **PDF** (.pdf) - Must be text-based, not scanned images
- **DOCX** (.docx) - Microsoft Word 2007+ format
- **TXT** (.txt) - Plain text with UTF-8 encoding

**Not supported**: .doc (legacy Word), .rtf, .odt, scanned PDFs without OCR

---

**Q: Why is there a 15,000 character limit?**

A: This is the maximum text length sent to the AI model for analysis. Documents longer than this are truncated. This limit ensures:
- Reasonable processing time
- Manageable AI costs
- Focus on main license content (usually in first sections)

Most standard licenses are under 15,000 characters. If truncated, you'll see a warning and can manually fill in terms from later sections.

---

**Q: Which AI models are supported?**

A: The application uses LiteLLM which supports multiple providers:
- OpenAI: GPT-4, GPT-4 Turbo, GPT-5
- Various LLM providers and models
- Others: Any model supported by your LiteLLM configuration

The specific model is configured by your system administrator.

---

**Q: Can I use this offline?**

A: No, the application requires:
- Internet connection for AI processing (LLM API)
- Internet connection for Alma API
- Web browser access to application server

---

**Q: What browsers are supported?**

A: Modern browsers with JavaScript enabled:
- **Google Chrome** 90+ (recommended)
- **Mozilla Firefox** 88+
- **Safari** 14+
- **Microsoft Edge** 90+

---

**Q: Is my data secure?**

A: Yes:
- All connections use HTTPS (in production)
- Session data is encrypted
- Uploaded files are deleted after processing
- Extracted text is deleted after submission
- API keys are stored server-side, never in browser

See SECURITY_GUIDE.md for full security details.

---

### Alma Integration Questions

**Q: Do I need special permissions in Alma?**

A: Your Alma API key must have:
- **Acquisitions**: Read/write permissions
- **Vendors**: Read permissions

Contact your Alma administrator if you lack these permissions.

---

**Q: Can I edit the license in Alma after submission?**

A: Yes! The License Uploader creates the initial license record with extracted terms. You can:
- Edit any terms in Alma
- Add notes and attachments
- Link to other records (vendors, portfolios, etc.)
- Update status and review information

---

**Q: What if the license code already exists in Alma?**

A: You'll get an error. License codes must be unique. Either:
- Use a different code
- Delete/rename the existing license in Alma
- Append a version number (e.g., LIC-2026-001-v2)

---

**Q: Does this replace the Alma license module?**

A: No, it complements it. The License Uploader:
- Automates initial extraction and entry
- Saves time on data entry
- Ensures standardized term codes

You still use Alma for:
- Final review and approval
- Ongoing license management
- Linking licenses to resources
- Reporting and renewals

---

### Error Recovery

**Q: What if processing fails midway?**

A:
1. Refresh the page
2. Upload the document again
3. If error persists, check:
   - Document is valid and readable
   - File size is under 16 MB
   - Internet connection is stable
4. Contact system administrator if issue continues

---

**Q: What if I accidentally submitted wrong information?**

A:
1. Log in to Alma
2. Find the license by code
3. Edit the license directly in Alma
4. Update any incorrect terms
5. Or delete the license and re-submit from License Uploader

---

**Q: Can I undo a submission?**

A: No, once submitted to Alma, the license is created. You must edit or delete it directly in Alma.

---

## Getting Help

### Documentation Resources

- **INSTALLATION_GUIDE.md**: Installation and setup instructions
- **DEPLOYMENT_GUIDE.md**: Production deployment guide
- **API_DOCUMENTATION.md**: API endpoint reference
- **SECURITY_GUIDE.md**: Security configuration
- **TROUBLESHOOTING_GUIDE.md**: Detailed troubleshooting

### Support Contacts

- **System Administrator**: For technical issues, API keys, server problems
- **Alma Administrator**: For Alma permissions, license management
- **Application Developer**: For bugs, feature requests

### Reporting Issues

When reporting issues, include:
1. What you were trying to do
2. What happened instead
3. Error message (exact text)
4. Browser and version
5. Screenshot (if applicable)
6. Document type and size (if upload-related)

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Document Owner**: Technical Writer Agent
