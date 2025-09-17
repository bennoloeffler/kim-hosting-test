#!/bin/bash
set -e

echo "========================================="
echo "🚀 Fly.io Deployment Script"
echo "========================================="
echo ""

APP_NAME="kim-hosting-test"

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found. Please run ./fly-launch.sh first"
    exit 1
fi

# Check if logged in
echo "🔐 Checking authentication..."
if ! fly auth whoami &> /dev/null; then
    echo "❌ Not authenticated. Please run:"
    echo "   fly auth login"
    exit 1
fi

echo "✅ Authenticated with Fly.io"

# Check if app exists
echo ""
echo "📦 Checking if app '$APP_NAME' exists..."
if ! fly apps list | grep -q "$APP_NAME"; then
    echo "❌ App '$APP_NAME' does not exist. Please run ./fly-launch.sh first"
    exit 1
fi

echo "✅ App '$APP_NAME' found"

# Check if secrets are configured
echo ""
echo "🔐 Checking if secrets are configured..."
if ! fly secrets list --app "$APP_NAME" | grep -q "EWS_CLIENT_ID"; then
    echo "⚠️  Secrets not configured. Please run ./fly-set-secrets.sh first"
    echo "   Continuing with deployment anyway..."
else
    echo "✅ Secrets are configured"
fi

# Deploy the application
echo ""
echo "🚀 Deploying application to Fly.io..."
echo "   This may take a few minutes..."
echo ""

fly deploy --app "$APP_NAME"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "========================================="
    echo "✅ Deployment successful!"
    echo "========================================="
    echo ""
    echo "🌐 Your app is available at: https://$APP_NAME.fly.dev"
    echo ""
    echo "🔧 Useful commands:"
    echo "   fly logs --app $APP_NAME        # View live logs"
    echo "   fly status --app $APP_NAME      # Check app status"
    echo "   fly open --app $APP_NAME        # Open in browser"
    echo "   fly ssh console --app $APP_NAME # SSH into container"
    echo "   fly scale --app $APP_NAME       # Scale app resources"
    echo ""
    echo "🧪 Test your deployment:"
    echo "   curl https://$APP_NAME.fly.dev/api/health"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Check the output above for errors."
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   • Check logs: fly logs --app $APP_NAME"
    echo "   • Verify secrets: fly secrets list --app $APP_NAME"
    echo "   • Check app status: fly status --app $APP_NAME"
    exit 1
fi