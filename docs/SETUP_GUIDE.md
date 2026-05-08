# Setup Guide — Step-by-Step

> **Last Updated:** 2026-05-02  
> **Estimated Time:** ~45 minutes total

---

## Part 1: API Keys (2 needed)

### 1A. OpenRouter API Key (provided by mentor)

**Cost:** $10 budget supporting DeepSeek V4 Flash + NVIDIA Nemotron-3 Super 120B

**Key:** Already provided via mentor — `sk-or-v1-...`

> **Save this key — set it as `OPENROUTER_API_KEY` environment variable**

### 1B. Groq API Key (~3 min)

**Cost:** Completely FREE (free tier gives 30 req/min for Llama-3.3-70B)

**Steps:**
1. Go to https://console.groq.com/
2. Click **"Sign Up"** — use Google/GitHub
3. After login, click **"API Keys"** in the left sidebar
4. Click **"Create API Key"**
5. Name it "cybergym-research"
6. Copy the key — it looks like: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

> **Save this key — you'll give it to me as `GROQ_API_KEY`**

---

## Part 2: AWS EC2 Setup (~30 min)

I can control the EC2 instance via SSH from your terminal. Here's exactly what to do:

### Step 1: Log into AWS Console
1. Go to https://console.aws.amazon.com/
2. Sign in with your AWS account (the one with $300 credits)
3. **Set region** to `us-east-1` (N. Virginia) — cheapest spot prices

### Step 2: Create an SSH Key Pair
1. Go to **EC2 Dashboard** → left sidebar → **Key Pairs**
2. Click **"Create key pair"**
3. Settings:
   - Name: `cybergym-key`
   - Type: **RSA**
   - Format: **.pem** (if on Windows, choose .ppk only if using PuTTY)
4. Click **Create** — it will auto-download `cybergym-key.pem`
5. **Move the .pem file** to your Desktop or a known location

### Step 3: Create a Security Group
1. Go to EC2 → left sidebar → **Security Groups**
2. Click **"Create security group"**
3. Settings:
   - Name: `cybergym-sg`
   - Description: `CyberGym research server`
   - VPC: default
4. **Inbound rules** — Add these:
   | Type | Port | Source | Purpose |
   |------|------|--------|---------|
   | SSH | 22 | My IP | SSH access |
   | Custom TCP | 8666 | 0.0.0.0/0 | CyberGym server |
5. Click **Create**

### Step 4: Launch EC2 Instance
1. Go to EC2 → **"Launch Instance"**
2. Settings:

   | Setting | Value |
   |---------|-------|
   | Name | `cybergym-research` |
   | AMI | **Ubuntu Server 24.04 LTS** (free tier eligible) |
   | Instance type | **c5.2xlarge** (8 vCPU, 16GB RAM) |
   | Key pair | `cybergym-key` (the one you just created) |
   | Security group | `cybergym-sg` |
   | Storage | **200 GB** gp3 (we need ~130GB for CyberGym data) |

3. **Optional but recommended:** Under "Advanced details" → "Purchasing option" → check **"Request Spot Instances"** to save ~70% ($0.10/hr instead of $0.34/hr)

4. Click **"Launch Instance"**

### Step 5: Get the Connection Info

Once the instance is running (takes ~2 min):

1. Go to **EC2 → Instances**
2. Click on your `cybergym-research` instance
3. Copy the **Public IPv4 address** (looks like `54.123.45.67`)

---

## Part 3: What to Give Me

Once you've completed Parts 1 and 2, provide me these 3 things:

```
1. DEEPSEEK_API_KEY = sk-xxxxxxxxxxxx
2. GROQ_API_KEY = gsk_xxxxxxxxxxxx
3. EC2 Public IP = 54.xxx.xxx.xxx
4. Path to your .pem key file on your local machine (e.g., C:\Users\ASUS\Desktop\cybergym-key.pem)
```

### What I'll Do With These

Using your terminal, I'll SSH into the EC2 instance and:

1. ✅ Install Docker, Python 3.11, Ollama, git-lfs
2. ✅ Clone CyberGym repo and install dependencies
3. ✅ Download CyberGym dataset (binary-only mode, ~130GB)
4. ✅ Start the CyberGym submission server
5. ✅ Clone our Prompting-Strategy repo
6. ✅ Set API keys as environment variables
7. ✅ Run the dataset filter to get our 100-instance subset
8. ✅ Run a pilot test (1 task, baseline prompt, DeepSeek-V3)
9. ✅ If pilot works → kick off full experiment batches

---

## Security Notes

> ⚠️ **About sharing API keys in chat:** 
> - DeepSeek key: Low risk — even if leaked, max exposure is $5-10 of credits
> - Groq key: Low risk — free tier, no billing
> - EC2 access: Protected by SSH key (.pem file) — I only access via your terminal
> - All keys will be stored as environment variables on EC2, never committed to git
> - After the project, you can rotate/delete all keys

---

## Quick Summary Checklist

- [ ] Sign up at platform.deepseek.com → get API key → add $5-10 balance
- [ ] Sign up at console.groq.com → get API key (free)
- [ ] Log into AWS Console → create key pair → create security group → launch c5.2xlarge
- [ ] Share with me: DeepSeek key, Groq key, EC2 IP, .pem file path
