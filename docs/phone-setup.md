# Phone Number Setup Guide

This guide explains how to configure a phone number so customers can call your Porsche Aftersales Support agent on a landline or mobile phone.

## Prerequisites

- An ElevenLabs account with Conversational AI access
- The agent must already be created (run `npm run setup` first)
- A Twilio account (for phone number provisioning) OR an existing SIP trunk

## Option 1: ElevenLabs Dashboard (Recommended)

1. Log in to [ElevenLabs](https://elevenlabs.io/app)
2. Navigate to **Conversational AI** in the left sidebar
3. Click **Phone Numbers**
4. Click **Add Phone Number**
5. Choose your provider:
   - **Twilio** — Connect your Twilio account and provision a number
   - **SIP Trunk** — Configure your existing SIP trunk
6. Once added, click the phone number and assign it to your **Porsche Aftersales Support** agent
7. Test by calling the number from any phone

## Option 2: Twilio Integration

### Step 1: Get a Twilio Phone Number

1. Sign up at [twilio.com](https://www.twilio.com)
2. Purchase a phone number with voice capability
3. Note your Account SID and Auth Token

### Step 2: Connect Twilio to ElevenLabs

1. In the ElevenLabs dashboard, go to **Phone Numbers**
2. Click **Add Phone Number** and select **Twilio**
3. Enter your Twilio Account SID, Auth Token, and phone number
4. ElevenLabs will configure the Twilio webhook automatically

### Step 3: Assign to Agent

1. Select the phone number in ElevenLabs
2. Choose your Porsche Aftersales Support agent from the dropdown
3. Save the configuration

## Option 3: SIP Trunk

If you have an existing phone system with SIP trunk capability:

1. In the ElevenLabs dashboard, go to **Phone Numbers**
2. Click **Add Phone Number** and select **SIP Trunk**
3. Configure your inbound SIP trunk settings:
   - SIP URI provided by ElevenLabs
   - Authentication credentials
4. Point your PBX/phone system to route calls to the ElevenLabs SIP URI
5. Assign the SIP trunk to your agent

## Testing

1. Call the assigned phone number from any phone
2. You should hear the Porsche greeting: "Thank you for calling Porsche Aftersales Support..."
3. Try asking about:
   - Service intervals for a specific model
   - Warranty coverage questions
   - Parts availability
   - Recall information
4. Monitor the conversation in the ElevenLabs dashboard under **Conversations**

## Monitoring and Logs

- **Dashboard**: View all conversations at ElevenLabs > Conversational AI > Conversations
- **Metrics**: Call duration, user satisfaction, and conversation counts are available in the Analytics tab
- **Transcripts**: Full transcripts of each conversation are available for review

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No audio when calling | Check that your Twilio number has voice capability enabled |
| Agent doesn't respond | Verify the agent is assigned to the phone number in the dashboard |
| Call drops immediately | Check your ElevenLabs API quota and billing status |
| Poor voice quality | Ensure your network has sufficient bandwidth; try a wired connection |
