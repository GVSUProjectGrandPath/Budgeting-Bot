import React, {useState, useEffect, useRef } from 'react';
import axios from 'axios';
import botAvatar from '../assests/bot.png';
import userAvatar from '../assets/user.png';
import '../styles.css';

export default function ChatWindow() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [theme, setTheme] = useState('light');
    const messagesEndRef = useRef(null);

    
}