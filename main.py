from app_fixed import *

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8002))
    app.run(host="0.0.0.0", port=port, debug=False)
