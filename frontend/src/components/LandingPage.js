import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Razorpay payment integration
const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
};

const LandingPage = ({ onLogin }) => {
  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [signupData, setSignupData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
    plan: 'Personal (₹2,000/month)',
    phone_number: ''
  });
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    company: '',
    plan: 'personal'
  });

  const plans = {
    personal: { name: 'Personal', price: 2000, features: ['Personal task management', 'AI task prioritization', 'Basic analytics', 'Mobile app access', 'Email support'] },
    team: { name: 'Team', price: 5000, features: ['Everything in Personal', 'Up to 25 team members', 'Project management & Kanban', 'Team performance analytics', 'AI productivity coach', 'Priority support'] },
    enterprise: { name: 'Enterprise', price: 7000, features: ['Everything in Team', 'Unlimited team members', 'Custom API integrations', 'WhatsApp Business API', 'Advanced AI features', '24/7 dedicated support', 'Custom training & onboarding'] }
  };

  const handlePayment = async (planType) => {
    const plan = plans[planType];
    setSelectedPlan({ ...plan, type: planType });
    
    // Load Razorpay script
    const isLoaded = await loadRazorpayScript();
    if (!isLoaded) {
      alert('Payment system failed to load. Please try again.');
      return;
    }

    try {
      // Create order
      const orderResponse = await axios.post(`${API}/payment/create-order`, {
        amount: plan.price * 100, // Convert to paise
        currency: 'INR',
        plan: planType
      });

      const options = {
        key: 'rzp_test_9WzaP4XKo0z9By', // Test key - replace with live key
        amount: orderResponse.data.amount,
        currency: orderResponse.data.currency,
        name: 'Productivity Beast',
        description: `${plan.name} Plan Subscription`,
        image: '/logo.png',
        order_id: orderResponse.data.id,
        handler: async (response) => {
          try {
            // Verify payment
            const verifyResponse = await axios.post(`${API}/payment/verify`, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan: planType
            });

            if (verifyResponse.data.success) {
              alert('Payment successful! Your account has been activated.');
              // Auto-create account and login
              const userData = verifyResponse.data.user;
              localStorage.setItem('token', verifyResponse.data.token);
              localStorage.setItem('user', JSON.stringify(userData));
              onLogin(userData);
            }
          } catch (error) {
            alert('Payment verification failed: ' + error.message);
          }
        },
        prefill: {
          name: formData.name,
          email: formData.email,
          contact: '9999999999'
        },
        notes: {
          plan: planType,
          company: formData.company
        },
        theme: {
          color: '#6366f1'
        }
      };

      const paymentObject = new window.Razorpay(options);
      paymentObject.open();
    } catch (error) {
      alert('Payment setup failed: ' + error.message);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if (signupData.password !== signupData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      // Convert plan display text to backend format
      let planValue = 'personal'; // default
      if (signupData.plan.includes('Team')) planValue = 'team';
      else if (signupData.plan.includes('Enterprise')) planValue = 'enterprise';
      
      const response = await axios.post(`${API}/auth/signup`, {
        name: signupData.name,
        email: signupData.email,
        password: signupData.password,
        company: signupData.company,
        plan: planValue
      });

      if (response.data.success) {
        alert('Account created successfully! Please login with your credentials.');
        setActiveTab('login');
        setSignupData({
          name: '',
          email: '',
          password: '',
          confirmPassword: '',
          company: '',
          plan: 'Personal (₹2,000/month)'
        });
      } else {
        alert('Failed to create account: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Signup error:', error);
      let errorMessage = 'Failed to create account';
      
      if (error.response) {
        if (error.response.status === 400) {
          errorMessage = error.response.data.detail || 'Invalid registration data';
        } else if (error.response.status === 422) {
          // Handle validation errors
          if (error.response.data.detail && Array.isArray(error.response.data.detail)) {
            const validationErrors = error.response.data.detail.map(err => err.msg).join(', ');
            errorMessage = 'Validation error: ' + validationErrors;
          } else {
            errorMessage = error.response.data.detail || 'Validation failed';
          }
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      alert(errorMessage);
    }
    setLoading(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: formData.email,
        password: formData.password
      });
      
      if (response.data.access_token) {
        // Store token and user data
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        setShowLogin(false);
        onLogin(response.data.user);
        
        alert('✅ Login successful! Welcome to Productivity Beast!');
      } else {
        alert('❌ Login failed: Invalid response from server');
      }
    } catch (error) {
      console.error('Login error:', error);
      let errorMessage = 'Login failed';
      
      if (error.response) {
        if (error.response.status === 401) {
          errorMessage = 'Invalid email or password';
        } else if (error.response.status === 422) {
          errorMessage = 'Please enter valid email and password';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      alert('❌ ' + errorMessage);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      {/* Facebook Pixel */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            !function(f,b,e,v,n,t,s)
            {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', 'YOUR_PIXEL_ID');
            fbq('track', 'PageView');
          `
        }}
      />
      
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Productivity Beast
              </h1>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setShowLogin(true)}
                className="btn-secondary"
              >
                Login
              </button>
              <button
                onClick={() => setShowSignup(true)}
                className="btn-primary"
              >
                Start Free Trial
              </button>
              
              {/* Quick Test Button */}
              <button
                onClick={async () => {
                  try {
                    console.log('🧪 Quick test login...');
                    const response = await axios.post(`${API}/auth/login`, {
                      email: 'test@example.com',
                      password: 'testpass123'
                    });
                    console.log('✅ Test login successful:', response.data);
                    if (response.data.access_token) {
                      localStorage.setItem('token', response.data.access_token);
                      localStorage.setItem('user', JSON.stringify(response.data.user));
                      onLogin(response.data.user);
                    }
                  } catch (error) {
                    console.error('❌ Test login failed:', error);
                    alert('Test login failed: ' + (error.response?.data?.detail || error.message));
                  }
                }}
                className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors text-sm"
              >
                🧪 Quick Test Login
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Transform Your Team's
            <span className="bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent"> Productivity</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered productivity management platform that combines personal task management, team collaboration, 
            and intelligent coaching to boost your organization's efficiency by 40%.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setShowSignup(true)}
              className="btn-primary text-lg px-8 py-4"
            >
              Start 14-Day Free Trial
            </button>
            <button className="btn-secondary text-lg px-8 py-4">
              Watch Demo
            </button>
          </div>
          <p className="text-gray-500 mt-4">✓ No credit card required ✓ Setup in 5 minutes ✓ Cancel anytime</p>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Everything You Need to Boost Productivity</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Comprehensive productivity suite with AI-powered insights, team collaboration, and smart automation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: "🎯",
              title: "AI-Powered Task Prioritization",
              description: "Eisenhower Matrix automation that categorizes tasks by urgency and importance, helping you focus on what matters most."
            },
            {
              icon: "👥",
              title: "Team Collaboration Hub",
              description: "Kanban boards, project management, and real-time collaboration tools that keep your team aligned and productive."
            },
            {
              icon: "📊",
              title: "Performance Analytics",
              description: "Advanced 1-10 performance scoring, completion tracking, and detailed insights to optimize team efficiency."
            },
            {
              icon: "🤖",
              title: "AI Productivity Coach",
              description: "Personalized coaching with pattern recognition, smart recommendations, and productivity insights tailored to your work style."
            },
            {
              icon: "📱",
              title: "WhatsApp Integration",
              description: "Seamless task notifications, status updates, and team communication through your existing WhatsApp Business API."
            },
            {
              icon: "🔗",
              title: "Custom API Integrations",
              description: "Connect your existing tools and workflows with our flexible API integration system for seamless productivity."
            }
          ].map((feature, index) => (
            <div key={index} className="stats-card text-center hover:scale-105 transition-transform">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Teams Choose Productivity Beast</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">40% Increase in Productivity</h4>
                    <p className="text-gray-600">AI-powered prioritization and smart workflows eliminate time waste</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Reduce Missed Deadlines by 85%</h4>
                    <p className="text-gray-600">Smart reminders and automated tracking keep projects on schedule</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Save 2+ Hours Daily</h4>
                    <p className="text-gray-600">Automated processes and intelligent insights eliminate manual overhead</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Improve Team Satisfaction by 60%</h4>
                    <p className="text-gray-600">Clear communication and balanced workloads boost team morale</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Transform Your Productivity?</h3>
                <p className="text-gray-600 mb-6">Join thousands of teams already boosting their efficiency with Productivity Beast.</p>
                <button
                  onClick={() => setShowSignup(true)}
                  className="btn-primary w-full text-lg py-3"
                >
                  Start Your Free Trial
                </button>
                <p className="text-gray-500 text-sm mt-3">14-day free trial • No credit card required</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Choose the perfect plan for your team size and needs. All plans include 14-day free trial.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Personal Plan */}
          <div className="stats-card text-center">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Personal</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">₹2,000<span className="text-lg text-gray-500">/month</span></div>
              <p className="text-gray-600">Perfect for individuals and freelancers</p>
            </div>
            
            <div className="space-y-3 text-left mb-6">
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Personal task management</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">AI task prioritization</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Basic analytics</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Mobile app access</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Email support</span>
              </div>
            </div>
            
            <button
              onClick={() => {
                setFormData({...formData, plan: 'personal'});
                handlePayment('personal');
              }}
              className="btn-secondary w-full"
            >
              Subscribe Now - ₹2,000/month
            </button>
          </div>

          {/* Team Plan */}
          <div className="stats-card text-center border-2 border-purple-500 relative">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-purple-500 text-white px-4 py-1 rounded-full text-sm font-medium">Most Popular</span>
            </div>
            
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Team</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">₹5,000<span className="text-lg text-gray-500">/month</span></div>
              <p className="text-gray-600">For growing teams and small businesses</p>
            </div>
            
            <div className="space-y-3 text-left mb-6">
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Everything in Personal</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Up to 25 team members</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Project management & Kanban</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Team performance analytics</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">AI productivity coach</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Priority support</span>
              </div>
            </div>
            
            <button
              onClick={() => {
                setFormData({...formData, plan: 'team'});
                handlePayment('team');
              }}
              className="btn-primary w-full"
            >
              Subscribe Now - ₹5,000/month
            </button>
          </div>

          {/* Enterprise Plan */}
          <div className="stats-card text-center">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Enterprise</h3>
              <div className="text-3xl font-bold text-purple-600 mb-2">₹7,000<span className="text-lg text-gray-500">/month</span></div>
              <p className="text-gray-600">For large organizations with advanced needs</p>
            </div>
            
            <div className="space-y-3 text-left mb-6">
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Everything in Team</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Unlimited team members</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Custom API integrations</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">WhatsApp Business API</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Advanced AI features</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">24/7 dedicated support</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">Custom training & onboarding</span>
              </div>
            </div>
            
            <button
              onClick={() => {
                setFormData({...formData, plan: 'enterprise'});
                handlePayment('enterprise');
              }}
              className="btn-secondary w-full"
            >
              Subscribe Now - ₹7,000/month
            </button>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-6">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Productivity?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Join thousands of teams who have already boosted their efficiency with Productivity Beast.
          </p>
          <button
            onClick={() => setShowSignup(true)}
            className="bg-white text-purple-600 font-semibold px-8 py-4 rounded-xl hover:bg-gray-50 transition-colors text-lg"
          >
            Start Your Free Trial Today
          </button>
          <p className="text-purple-200 mt-4">14-day free trial • No setup fees • Cancel anytime</p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold">Productivity Beast</h3>
              </div>
              <p className="text-gray-400">
                AI-powered productivity management platform for modern teams.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">API</a></li>
                <li><a href="#" className="hover:text-white">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">User Guide</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
                <li><a href="#" className="hover:text-white">Community</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Productivity Beast. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold">Welcome Back</h3>
              <button
                onClick={() => setShowLogin(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="input-field"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="input-field"
                  placeholder="Enter your password"
                  required
                />
              </div>

              <button type="submit" className="btn-primary w-full">
                Sign In
              </button>
            </form>

            <p className="text-center text-gray-600 mt-4">
              Don't have an account?{' '}
              <button
                onClick={() => {
                  setShowLogin(false);
                  setShowSignup(true);
                }}
                className="text-purple-600 hover:text-purple-700"
              >
                Sign up
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Signup Modal */}
      {showSignup && (
        <div className="modal-overlay" onClick={() => setShowSignup(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold">Start Your Free Trial</h3>
              <button
                onClick={() => setShowSignup(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSignup} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={signupData.name}
                    onChange={(e) => setSignupData({...signupData, name: e.target.value})}
                    className="input-field"
                    placeholder="Enter your name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
                  <input
                    type="text"
                    value={signupData.company}
                    onChange={(e) => setSignupData({...signupData, company: e.target.value})}
                    className="input-field"
                    placeholder="Company name"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={signupData.email}
                  onChange={(e) => setSignupData({...signupData, email: e.target.value})}
                  className="input-field"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">WhatsApp Number (Optional)</label>
                <input
                  type="tel"
                  value={signupData.phone_number}
                  onChange={(e) => setSignupData({...signupData, phone_number: e.target.value})}
                  className="input-field"
                  placeholder="e.g., +91 98765 43210"
                />
                <p className="text-xs text-gray-500 mt-1">For task notifications and team messaging</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input
                    type="password"
                    value={signupData.password}
                    onChange={(e) => setSignupData({...signupData, password: e.target.value})}
                    className="input-field"
                    placeholder="Create a password"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
                  <input
                    type="password"
                    value={signupData.confirmPassword}
                    onChange={(e) => setSignupData({...signupData, confirmPassword: e.target.value})}
                    className="input-field"
                    placeholder="Confirm password"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Plan</label>
                <select
                  value={signupData.plan}
                  onChange={(e) => setSignupData({...signupData, plan: e.target.value})}
                  className="select-field"
                >
                  <option value="Personal (₹2,000/month)">Personal (₹2,000/month)</option>
                  <option value="Team (₹5,000/month)">Team (₹5,000/month)</option>
                  <option value="Enterprise (₹7,000/month)">Enterprise (₹7,000/month)</option>
                </select>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full">
                {loading ? 'Creating Account...' : 'Start 14-Day Free Trial'}
              </button>
            </form>

            <p className="text-center text-gray-600 mt-4 text-sm">
              Already have an account?{' '}
              <button
                onClick={() => {
                  setShowSignup(false);
                  setShowLogin(true);
                }}
                className="text-purple-600 hover:text-purple-700"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;