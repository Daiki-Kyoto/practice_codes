"""画像URLを管理"""
url_head = "https://drive.google.com/uc?id="

image_ids = [
    ["1eUO6Q2DAamkYFjwa8EZE8ZRwYcPjQg36", "1G1lf3UbysGMg1pM_QzJlyU88-3BZTKiI"],
    ["1FHGfHlctYkOTQlwCzv0jTQpZGtduBE3O", "1O8_Yeccd-Oi-A6x9KWbWRHt_q6u0TR3N"],
    ["1D3MRoHc8GL6DyDnhc-pcQL2ONJnKiqMi", "1tE4G0DkldDHxhiFKObSJOqWUeKxX5N0w"],
    ["1DG8LOYkS3EPg-6XuYL1qdLdWphd6hVG_", "1ALha-U-3ZOEmmVsGml9cxNl6GZpkBnVy"],
    ["1VRpNrLp2JnMjbVa2_DOXYGF6r6Ykshch", "1y7n6djrcZVInk1CMo2x2Ka6sdf8qFFAa"],
    ["1_tv2SMLNRuts0r2LOurY3NY5b9n6SgkN", "1eKPmr8v_tNk5c56ZR7KlP_6tC1B5DemN"],
    ["1BMvNWzq9eO2kTVI8PTpjBkKoeEayMULO", "1YlZbZc1vtsOYy1FAUUff-0CZaovgmOVs"],
    ["1tzSU_miz3uxiihsopPP_Wlf8RqD6lAZ5", "1mxfvPwpJ2sHSX6BPrzbuUmle3v0LVqNo"],
    ["1wQoLS11-jIUkz8ix9XNOeqNes_iMJEjr", "18lOLOM5ePNBzYphWSt5e7KlflEQVuT7m"],
    ["1Xl_s_-Qu9ChlVQzdIwFlM3PjLvOukI7-", "1viGETfmhZtxyZrs1UTy0JVxJ4DJ8YDt0"],
    ["1jC1nL9-zyKuEZ7PS0HsyN6SZnn7kh1Tm", "1z0RkN08Vwougwxb_bzzhY3CrYtBjsTyl"],
    ["1c9gRa4jsKcLAIfz6DBXC0KqAMsyx8H7d", "1H6RIy8SMZRQSQMcFp2VM11gTp8Y9FHLh"],
    ["1KFV3-rPkgqIgVLrL8cS8vYkIyfN4ocvJ", "1o6OZXq12tKiw8pJcBqz0ha2txiverwE4"]
]

image_urls = [[url_head + j for j in i] for i in image_ids]
