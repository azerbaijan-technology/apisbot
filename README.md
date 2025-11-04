# Apisbot - Telegram Natal Chart Bot

A Telegram bot that generates personalized natal (birth) charts based on user-provided birth information.

## Features

- Interactive conversation flow to collect birth data
- Support for multiple date and time formats
- Automatic location geocoding
- Beautiful natal chart generation using Kerykeion
- SVG to PNG conversion for easy sharing
- Privacy-focused: all user data is deleted after chart generation
- Session timeout for security
- Comprehensive error handling and validation

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd apisbot
```

2. Install dependencies:
```bash
make install
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set your bot token:
```env
BOT_TOKEN=your_bot_token_from_botfather
LOG_LEVEL=INFO
SESSION_TIMEOUT=1800
```

## Usage

### Running the Bot

Start the bot locally:
```bash
make run
```

### Development Commands

The project uses a Makefile for common tasks:

- `make help` - Show all available commands
- `make install` - Install all dependencies using uv
- `make test` - Run the test suite with pytest
- `make lint` - Run type checking with pyright
- `make all` - Run both linting and tests
- `make clean` - Remove build artifacts and caches
- `make run` - Start the Telegram bot

### Docker

Build and run with Docker:
```bash
docker build -t apisbot .
docker run -d --env-file .env apisbot
```

## Bot Commands

- `/start` - Begin generating a natal chart
- `/help` - Show help and usage instructions
- `/cancel` - Cancel current operation and clear data

## Supported Date Formats

- **YYYY-MM-DD** (e.g., 1990-05-15)
- **DD/MM/YYYY** (e.g., 15/05/1990)
- **Month DD, YYYY** (e.g., May 15, 1990)
- **DD Month YYYY** (e.g., 15 May 1990)

## Supported Time Formats

- **24-hour: HH:MM** (e.g., 14:30)
- **12-hour: HH:MM AM/PM** (e.g., 2:30 PM)
- **Hour only: HH** (e.g., 14 or 2 PM)

## Privacy

This bot is designed with privacy in mind:
- All user data is stored only in memory during the conversation
- Data is automatically deleted after chart generation
- Sessions expire after 30 minutes of inactivity (configurable)
- No persistent storage of personal information

## Development

### Type Checking

The project uses pyright for type checking:
```bash
make lint
```

### Testing

Run the test suite:
```bash
make test
```

### Code Style

The project follows standard Python conventions with type checking enabled. All code should pass pyright checks in basic mode.

## Configuration

Configuration is managed through environment variables (see `.env.example`):

- `BOT_TOKEN` - Your Telegram bot token (required)
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `SESSION_TIMEOUT` - Session timeout in seconds (default: 1800)

## Architecture

The bot uses:
- **FSM (Finite State Machine)** for conversation flow management
- **Middleware** for cross-cutting concerns (logging, etc.)
- **Service layer** for business logic separation
- **Pydantic models** for data validation
- **Async/await** throughout for optimal performance

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

## Support

[Add support information here]
