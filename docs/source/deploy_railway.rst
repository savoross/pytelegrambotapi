====================
Deploying on Railway
====================

.. meta::
   :description: Deploying pyTelegramBotAPI bots on Railway
   :keywords: pyTelegramBotAPI, Railway, deployment, hosting

This guide shows a minimal example of running a bot on `Railway <https://railway.app>`_.

1. Create a new **Python** project on Railway.
2. Add your bot code (for example :download:`examples/echo_bot.py <../../examples/echo_bot.py>`)
   to the repository. Place your token in an environment variable named ``BOT_TOKEN``.
3. Set the start command to ``python echo_bot.py``.
4. In ``requirements.txt`` include ``pyTelegramBotAPI``.
5. Deploy the project. Your bot will start polling for updates.
