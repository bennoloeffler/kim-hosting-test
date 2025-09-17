#!/bin/bash
set -e

echo "========================================="
echo "🚀 Fly.io App Launch Script"
echo "========================================="
echo ""

APP_NAME="kim-hosting-test"
REGION="fra"

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found. Installing..."
    echo ""
    curl -L https://fly.io/install.sh | sh

    # Add to PATH for current session
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"

    echo ""
    echo "✅ Fly CLI installed successfully"
    echo "💡 You may need to restart your terminal or run:"
    echo "   export PATH=\"\$HOME/.fly/bin:\$PATH\""
    echo ""
else
    echo "✅ Fly CLI is already installed"
fi

# Check if logged in
echo "🔐 Checking authentication..."
if ! fly auth whoami &> /dev/null; then
    echo ""
    echo "📝 Please login to Fly.io first:"
    echo "   Opening browser for authentication..."
    echo ""
    fly auth login
    echo ""
    echo "✅ Authentication completed"
else
    echo "✅ Already authenticated with Fly.io"
fi

echo ""
echo "📦 Checking if app '$APP_NAME' exists..."

# Check if app exists
if fly apps list | grep -q "$APP_NAME"; then
    echo "✅ App '$APP_NAME' already exists"
    echo ""
    echo "📋 App status:"
    fly status --app "$APP_NAME" || echo "   (App may not be deployed yet)"
else
    echo ""
    echo "🆕 Creating new Fly app '$APP_NAME'..."
    echo "   Region: $REGION"
    echo ""

    # Create app without deploying
    fly launch --name "$APP_NAME" --region "$REGION" --no-deploy

    echo ""
    echo "✅ App '$APP_NAME' created successfully"
fi

echo ""
echo "========================================="
echo "✅ Launch setup complete!"
echo "========================================="
echo ""
echo "📋 Next steps:"
echo "   1. Configure secrets: ./fly-set-secrets.sh"
echo "   2. Deploy your app:   ./fly-deploy.sh"
echo ""
echo "🔧 Useful commands:"
echo "   fly status --app $APP_NAME      # Check app status"
echo "   fly logs --app $APP_NAME        # View logs"
echo "   fly open --app $APP_NAME        # Open in browser"
echo "   fly ssh console --app $APP_NAME # SSH into container"
echo ""