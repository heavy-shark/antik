# 📥 Excel Profile Import - Complete Guide

## ✅ Feature Added!

You can now import multiple profiles from an Excel file with email, password, proxy, and 2FA secret!

---

## 📋 Excel File Format

### Required Structure:

```
Row 1 (Headers):  email  |  password  |  proxy  |  2fa_secret
Row 2:            user1@example.com  |  pass123  |  123.45.67.89:8080  |  JBSWY3DPEHPK3PXP
Row 3:            user2@gmail.com    |  pass456  |  proxy.com:3128     |  MFRGGZDFMZTWQ2LK
Row 4:            ...
```

### Column Details:

| Column | Name | Required | Description | Example |
|--------|------|----------|-------------|---------|
| A | email | ✅ Yes | Email address (used as profile identifier) | `user@example.com` |
| B | password | ❌ Optional | Account password | `myPassword123` |
| C | proxy | ❌ Optional | Proxy server address | `123.45.67.89:8080` |
| D | 2fa_secret | ❌ Optional | 2FA/TOTP secret key | `JBSWY3DPEHPK3PXP` |

**Important:**
- Row 1 MUST contain headers (will be skipped)
- Data starts from Row 2
- Email is REQUIRED - rows without email will be skipped
- Other fields are optional (can be empty)

---

## 🚀 How to Import Profiles

### Step 1: Prepare Your Excel File

Create an Excel file (.xlsx or .xls) with the format above.

**Option A: Use the Sample File** (Already created!)
```
📁 C:\Users\daniel\Desktop\profiles_sample.xlsx
```

**Option B: Create Your Own**
1. Open Excel or Google Sheets
2. Add headers in Row 1: `email | password | proxy | 2fa_secret`
3. Add your data starting from Row 2
4. Save as `.xlsx`

### Step 2: Import to App

1. **Open the app**
   ```
   Double-click START_APP.bat
   ```

2. **Go to "Profiles" tab**

3. **Click the green button:**
   ```
   📥 Import Profiles from Excel
   ```

4. **Select your Excel file**
   - File dialog opens
   - Navigate to your Excel file
   - Click "Open"

5. **Confirm the import**
   - Review the file path
   - Click "Yes" to proceed

6. **View results**
   - Success message shows:
     - ✅ How many profiles imported
     - ⚠️ How many skipped
     - Any errors/warnings

---

## 📊 Example Excel Files

### Example 1: Full Data
```
email                   | password    | proxy              | 2fa_secret
user1@example.com      | pass123     | 123.45.67.89:8080  | JBSWY3DPEHPK3PXP
user2@gmail.com        | pass456     | proxy.com:3128     | MFRGGZDFMZTWQ2LK
```

### Example 2: Partial Data (Some Fields Empty)
```
email                   | password    | proxy              | 2fa_secret
user1@example.com      | pass123     |                    | JBSWY3DPEHPK3PXP
user2@gmail.com        | pass456     | 123.45.67.89:8080  |
user3@test.com         |             |                    |
```

### Example 3: MEXC Accounts
```
email                   | password       | proxy              | 2fa_secret
trader1@mexc.com       | mexcPass1      | 45.67.89.12:1080   | GEZDGNBVGY3TQOJQ
trader2@mexc.com       | mexcPass2      |                    | MFRGGZDFMZTWQ2LK
```

---

## 🎯 Profile Naming

Profiles are automatically named based on the email:

| Email | Profile Name |
|-------|-------------|
| `user@example.com` | `user_at_example_com` |
| `trader1@mexc.com` | `trader1_at_mexc_com` |
| `my.email@gmail.com` | `my_email_at_gmail_com` |

- `@` → `_at_`
- `.` → `_`

---

## ✅ What Gets Imported

Each imported profile contains:

- ✅ **Profile name** (auto-generated from email)
- ✅ **Email** (stored securely)
- ✅ **Password** (stored, shown as `***` in UI)
- ✅ **Proxy** (stored, shown in profile details)
- ✅ **2FA Secret** (stored, shown as `***` in UI)
- ✅ **Description** (auto: "Imported from Excel (Row X)")
- ✅ **Browser profile folder** (for cookies, sessions, etc.)

---

## 📝 Import Behavior

### ✅ Successfully Imported When:
- Email is present and valid
- Profile with same email doesn't exist yet

### ⚠️ Skipped When:
- Email is missing or empty
- Profile with that email already exists
- Row is completely empty

### ❌ Error Handling:
- Errors are logged and shown in results
- Import continues even if some rows fail
- Only first 10 errors shown (to avoid overwhelming)

---

## 💡 Tips & Best Practices

### Tip 1: Test with Sample File First
```bash
cd C:\Users\daniel\Desktop\hysk.pro\antik
python create_sample_excel.py
```
This creates `profiles_sample.xlsx` on your Desktop with 5 test profiles.

### Tip 2: Backup Before Import
The app doesn't overwrite existing profiles, but it's good practice to backup:
```
Backup location: %USERPROFILE%\.botasaurus\profiles\profiles_metadata.json
```

### Tip 3: Use Descriptive Emails
Make emails descriptive so you know which account is which:
- ✅ `trader1@mexc.com`
- ✅ `account_main@gmail.com`
- ❌ `a@b.com` (hard to identify)

### Tip 4: Empty Fields Are OK
You don't need all fields filled:
```
email                | password  | proxy  | 2fa_secret
user@example.com    | pass123   |        |              ← Valid!
```

### Tip 5: Check Import Results
Always review the import summary:
- Number of successful imports
- Number of skipped
- Any error messages

---

## 🔍 Viewing Imported Profiles

After import:

1. **In Profiles List**
   - All imported profiles appear in the list
   - Named like: `user_at_example_com`

2. **Select a Profile to View Details**
   - Email: Shows actual email
   - Password: Shows `***` (hidden)
   - Proxy: Shows proxy if set, or `N/A`
   - 2FA Secret: Shows `***` (hidden)
   - Created date
   - Import description

3. **Click "ℹ️ Profile Info" Button**
   - Shows full details in popup
   - Still hides password/2FA for security

---

## 🧪 Testing

### Quick Test:

1. Run the sample creator:
   ```bash
   cd C:\Users\daniel\Desktop\hysk.pro\antik
   python create_sample_excel.py
   ```

2. Launch the app:
   ```
   Double-click START_APP.bat
   ```

3. Import the sample:
   - Profiles tab
   - Click "📥 Import Profiles from Excel"
   - Select `C:\Users\daniel\Desktop\profiles_sample.xlsx`
   - Confirm

4. Expected result:
   ```
   ✅ Successfully imported: 5 profiles
   ⚠️ Skipped: 0 profiles
   ```

5. Check profiles:
   - Should see 5 new profiles in list
   - Select each to view details
   - Email, password, proxy, 2FA should be stored

---

## 🚨 Troubleshooting

### Problem: "No profiles were imported"
- **Check:** Excel file has data in Row 2+
- **Check:** Column A (email) is not empty
- **Check:** Headers are in Row 1

### Problem: "All profiles skipped"
- **Reason:** Profiles already exist
- **Solution:** Delete existing profiles or use different emails

### Problem: "Failed to read Excel file"
- **Check:** File is .xlsx or .xls format
- **Check:** File is not open in Excel
- **Check:** File is not corrupted

### Problem: "Some profiles imported, others skipped"
- **Normal!** Check the error list
- **Common reasons:**
  - Missing emails in some rows
  - Duplicate emails
  - Empty rows

---

## 📂 Where Data is Stored

### Profile Metadata:
```
%USERPROFILE%\.botasaurus\profiles\profiles_metadata.json
```

Contains:
- Profile names
- Emails, passwords, proxies, 2FA secrets
- Created/last used dates
- Paths to browser folders

### Browser Data:
```
%USERPROFILE%\.botasaurus\profiles\{profile_name}\
```

Contains:
- Cookies
- Sessions
- localStorage
- Browser cache

---

## 🎉 You're Ready!

**To create your sample Excel file:**
```bash
cd C:\Users\daniel\Desktop\hysk.pro\antik
python create_sample_excel.py
```

**To import:**
1. Open app (START_APP.bat)
2. Profiles tab
3. Click "📥 Import Profiles from Excel"
4. Select your .xlsx file
5. Done!

Enjoy mass-importing your profiles! 🚀
