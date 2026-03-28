# Phase 4 Testing Guide - GitHub Integration

## 🎯 What's New in Phase 4

### Features Implemented
- ✅ GitHub repository input (required)
- ✅ GitHub token authentication (required)
- ✅ File selection with checkboxes
- ✅ Pagination (20 files per page)
- ✅ Search functionality
- ✅ File type filter
- ✅ Smart changed file detection
- ✅ Auto-select modified files
- ✅ Commit SHA tracking
- ✅ Per-file analysis

---

## 🚀 How to Test

### Step 1: Start Streamlit

```bash
streamlit run main.py
```

### Step 2: Enter API Keys

**In the sidebar:**
1. **Groq API Key** - Your existing key (already in .env)
2. **GitHub Token** - Get from https://github.com/settings/tokens (needs repo access)

### Step 3: Test with Your Repository

**Option A: Use Your Repo (Recommended)**
1. Enter: `https://github.com/Kaushik-SPACEZ/github-agent`
2. Click "🔍 Fetch Repository"
3. Wait for files to load

**Option B: Use Example Button**
1. Click "💡 Use Example"
2. Automatically fills in your repo URL
3. Click "🔍 Fetch Repository"

---

## ✅ Expected Behavior

### First Time Analysis

**What Should Happen:**
1. ✅ Message: "First analysis! Fetched X files"
2. ✅ All files shown (none selected by default)
3. ✅ No 🔴 badges (no changed files yet)
4. ✅ Pagination shows 20 files per page
5. ✅ Search and filter work

**Test Actions:**
- [ ] Search for "main.py" - should filter files
- [ ] Filter by ".py" - should show only Python files
- [ ] Click "✅ Select All" - all visible files selected
- [ ] Click "❌ Clear Selection" - all deselected
- [ ] Manually select 2-3 files
- [ ] Click "🚀 Analyze X Selected Files"

### Subsequent Analysis (After First Run)

**What Should Happen:**
1. ✅ Message: "Fetched X files. Y files changed since last analysis"
2. ✅ Changed files have 🔴 **Modified** badge
3. ✅ Changed files auto-selected
4. ✅ Can add/remove selections

**Test Actions:**
- [ ] Click "🔴 Select Changed Only" - only modified files selected
- [ ] Verify changed files have red badge
- [ ] Add more files to selection
- [ ] Run analysis

---

## 📊 UI Components to Verify

### Sidebar
- [ ] Groq API Key input (password field)
- [ ] GitHub Token input (password field)
- [ ] Warning if keys missing
- [ ] Model selection dropdown
- [ ] Repository stats (after fetch):
  - Total Files
  - Changed Files
  - Selected

### Main Area - Step 1
- [ ] GitHub Repository URL input
- [ ] "🔍 Fetch Repository" button (primary)
- [ ] "💡 Use Example" button
- [ ] Success/error messages

### Main Area - Step 2 (After Fetch)
- [ ] Search box (filters files)
- [ ] File type filter (multiselect)
- [ ] Quick action buttons:
  - ✅ Select All
  - 🔴 Select Changed Only
  - ❌ Clear Selection
  - Page number input
- [ ] File list with checkboxes
- [ ] 🔴 Modified badge on changed files
- [ ] File size display
- [ ] Pagination info (showing X-Y of Z)
- [ ] "🚀 Analyze X Selected Files" button

### Main Area - Step 3 (During Analysis)
- [ ] Spinner: "Fetching file contents..."
- [ ] Success message: "Fetched X files"
- [ ] Spinner: "Analyzing code quality..."
- [ ] Results display
- [ ] Download button

---

## 🧪 Test Scenarios

### Scenario 1: First Time User

```
1. Open Streamlit
2. Enter both API keys
3. Enter repo URL: https://github.com/Kaushik-SPACEZ/github-agent
4. Click "Fetch Repository"
5. See: "First analysis! Fetched 25 files"
6. Search for "main"
7. See filtered results
8. Select 2 files
9. Click "Analyze 2 Selected Files"
10. Wait for analysis
11. See results
```

**Expected:** ✅ Works smoothly, no errors

### Scenario 2: Subsequent Analysis

```
1. Open Streamlit (after Scenario 1)
2. Same repo URL
3. Click "Fetch Repository"
4. See: "Fetched 25 files. 0 files changed" (if no changes)
5. Or: "X files changed since last analysis" (if changes)
6. Changed files auto-selected with 🔴 badge
7. Click "Select Changed Only"
8. Analyze
```

**Expected:** ✅ Detects changes correctly

### Scenario 3: Large Repository

```
1. Use a repo with 50+ files
2. Fetch repository
3. See pagination (Page 1/3)
4. Navigate to page 2
5. Select files on page 2
6. Go back to page 1
7. Selections preserved
8. Analyze
```

**Expected:** ✅ Pagination works, selections persist

### Scenario 4: Search & Filter

```
1. Fetch repository
2. Search: "test"
3. See only files with "test" in name
4. Clear search
5. Filter by: .py
6. See only Python files
7. Filter by: .py, .md
8. See Python and Markdown files
9. Select and analyze
```

**Expected:** ✅ Search and filter work correctly

### Scenario 5: Error Handling

```
Test A: Missing API Keys
1. Clear API keys
2. Try to fetch
3. See: "Both API keys are required!"

Test B: Invalid Repo URL
1. Enter: "https://github.com/invalid/repo"
2. Click fetch
3. See error message

Test C: No Files Selected
1. Fetch repository
2. Clear all selections
3. See: "No files selected" warning
4. Analyze button disabled or shows warning
```

**Expected:** ✅ Clear error messages

---

## 🐛 Known Issues to Check

### Issue 1: Session State
**Problem:** Selections lost on page change
**Test:** Select files on page 1, go to page 2, come back
**Expected:** Selections preserved

### Issue 2: Commit Tracking
**Problem:** commit_tracker.json not updating
**Test:** Run analysis, check commit_tracker.json file
**Expected:** File updated with commit SHA

### Issue 3: Changed Files Detection
**Problem:** Not detecting changes
**Test:** Analyze, make a change, push, fetch again
**Expected:** Shows changed files with 🔴 badge

---

## 📝 Checklist Before Marking Complete

### Functionality
- [ ] Fetch repository works
- [ ] File list displays correctly
- [ ] Pagination works (20 per page)
- [ ] Search filters files
- [ ] File type filter works
- [ ] Select All works
- [ ] Select Changed Only works
- [ ] Clear Selection works
- [ ] Checkboxes update selections
- [ ] Analysis runs on selected files
- [ ] Results display correctly
- [ ] Commit SHA saved to commit_tracker.json

### UI/UX
- [ ] No console errors
- [ ] Buttons are responsive
- [ ] Loading spinners show
- [ ] Success/error messages clear
- [ ] File badges visible
- [ ] Pagination intuitive
- [ ] Search is fast

### Edge Cases
- [ ] Works with 0 files
- [ ] Works with 100+ files
- [ ] Works with no changes
- [ ] Works with all files changed
- [ ] Handles API errors gracefully
- [ ] Handles network errors

---

## 🎯 Success Criteria

Phase 4 is complete when:

1. ✅ User can enter GitHub repo URL
2. ✅ User can enter GitHub token
3. ✅ Repository fetches successfully
4. ✅ All files display with pagination
5. ✅ Search and filter work
6. ✅ Changed files auto-detected
7. ✅ Changed files auto-selected
8. ✅ User can manually select files
9. ✅ Analysis runs on selected files only
10. ✅ Results display per file
11. ✅ Commit SHA saved for next time
12. ✅ No critical bugs

---

## 🚀 Quick Test Commands

```bash
# Start Streamlit
streamlit run main.py

# Check commit tracker
cat commit_tracker.json

# View logs (if errors)
# Check terminal output
```

---

## 📊 Test Results Template

```
Date: ___________
Tester: ___________

Scenario 1 (First Time): ☐ Pass ☐ Fail
Scenario 2 (Subsequent): ☐ Pass ☐ Fail
Scenario 3 (Large Repo): ☐ Pass ☐ Fail
Scenario 4 (Search/Filter): ☐ Pass ☐ Fail
Scenario 5 (Error Handling): ☐ Pass ☐ Fail

Critical Bugs Found: ___________
Minor Issues: ___________

Overall Status: ☐ Ready for Phase 5 ☐ Needs Fixes
```

---

## 🎉 Next Steps After Testing

If all tests pass:
1. ✅ Mark Phase 4 as complete
2. ✅ Update PROJECT_STATUS.md
3. ✅ Commit changes to GitHub
4. 🔄 Start Phase 5: Jira Integration

If tests fail:
1. 🐛 Document bugs
2. 🔧 Fix issues
3. 🧪 Re-test
4. ✅ Repeat until all pass

---

**Ready to test! Run `streamlit run main.py` and follow the scenarios above.** 🚀