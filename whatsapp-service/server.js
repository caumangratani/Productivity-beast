const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const express = require('express')
const cors = require('cors')
const axios = require('axios')
const { v4: uuidv4 } = require('uuid')

const app = express()
app.use(cors())
app.use(express.json())

const FASTAPI_URL = process.env.FASTAPI_URL || 'https://ee90ce40-e7e1-4fc3-b144-06755894b42a.preview.emergentagent.com'

let sock = null
let qrCode = null
let connectionStatus = 'disconnected'
let connectedUser = null

async function initWhatsApp() {
    try {
        console.log('🚀 Initializing WhatsApp connection...')
        
        const { state, saveCreds } = await useMultiFileAuthState('auth_info')

        sock = makeWASocket({
            auth: state,
            printQRInTerminal: false,
            browser: ['Productivity Beast', 'Chrome', '1.0.0'],
            defaultQueryTimeoutMs: 60000
        })

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update

            if (qr) {
                qrCode = qr
                connectionStatus = 'qr_ready'
                console.log('📱 QR Code generated for WhatsApp authentication')
            }

            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut
                console.log('❌ Connection closed:', lastDisconnect?.error?.output?.statusCode, ', reconnecting:', shouldReconnect)
                
                connectionStatus = 'disconnected'
                connectedUser = null
                qrCode = null

                if (shouldReconnect) {
                    setTimeout(initWhatsApp, 5000)
                }
            } else if (connection === 'open') {
                console.log('✅ WhatsApp connected successfully!')
                connectionStatus = 'connected'
                connectedUser = sock.user
                qrCode = null
                
                // Send welcome message to connected user
                await sendMessage(sock.user.id, '🤖 *Productivity Beast WhatsApp Bot Connected!*\n\nYou can now manage your tasks via WhatsApp. Type *help* to see available commands.')
            }
        })

        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            if (type === 'notify') {
                for (const message of messages) {
                    if (!message.key.fromMe && message.message) {
                        await handleIncomingMessage(message)
                    }
                }
            }
        })

        sock.ev.on('creds.update', saveCreds)

    } catch (error) {
        console.error('❌ WhatsApp initialization error:', error)
        connectionStatus = 'error'
        setTimeout(initWhatsApp, 10000)
    }
}

async function handleIncomingMessage(message) {
    try {
        const phoneNumber = message.key.remoteJid.replace('@s.whatsapp.net', '')
        const messageText = message.message.conversation ||
                           message.message.extendedTextMessage?.text || ''

        console.log(`📨 Received message from ${phoneNumber}: ${messageText}`)

        // Forward message to FastAPI for processing
        const response = await axios.post(`${FASTAPI_URL}/api/whatsapp/message`, {
            phone_number: phoneNumber,
            message: messageText,
            message_id: message.key.id,
            timestamp: message.messageTimestamp
        })

        // Send response back to WhatsApp if FastAPI returns one
        if (response.data.reply) {
            await sendMessage(phoneNumber, response.data.reply)
        }

    } catch (error) {
        console.error('❌ Error handling incoming message:', error)
        
        // Send error message to user
        const phoneNumber = message.key.remoteJid.replace('@s.whatsapp.net', '')
        await sendMessage(phoneNumber, '❌ Sorry, I encountered an error processing your message. Please try again.')
    }
}

async function sendMessage(phoneNumber, text) {
    try {
        if (!sock || connectionStatus !== 'connected') {
            throw new Error('WhatsApp not connected')
        }

        const jid = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`
        await sock.sendMessage(jid, { text })
        console.log(`📤 Message sent to ${phoneNumber}`)
        return { success: true }

    } catch (error) {
        console.error('❌ Error sending message:', error)
        return { success: false, error: error.message }
    }
}

// REST API endpoints
app.get('/qr', async (req, res) => {
    try {
        res.json({ 
            qr: qrCode || null,
            status: connectionStatus,
            user: connectedUser
        })
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

app.post('/send', async (req, res) => {
    const { phone_number, message } = req.body
    
    if (!phone_number || !message) {
        return res.status(400).json({ error: 'Phone number and message are required' })
    }
    
    const result = await sendMessage(phone_number, message)
    res.json(result)
})

app.get('/status', (req, res) => {
    res.json({
        connected: connectionStatus === 'connected',
        status: connectionStatus,
        user: connectedUser,
        qr_available: !!qrCode
    })
})

app.post('/restart', async (req, res) => {
    try {
        console.log('🔄 Restarting WhatsApp connection...')
        if (sock) {
            sock.end()
        }
        setTimeout(initWhatsApp, 2000)
        res.json({ message: 'WhatsApp connection restart initiated' })
    } catch (error) {
        res.status(500).json({ error: error.message })
    }
})

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        whatsapp_status: connectionStatus,
        timestamp: new Date().toISOString()
    })
})

const PORT = process.env.PORT || 3001
app.listen(PORT, () => {
    console.log(`🌐 WhatsApp service running on port ${PORT}`)
    console.log(`📱 FastAPI URL: ${FASTAPI_URL}`)
    
    // Initialize WhatsApp connection
    initWhatsApp()
})

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('🛑 Shutting down WhatsApp service...')
    if (sock) {
        sock.end()
    }
    process.exit(0)
})