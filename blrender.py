# -*- coding: utf-8 -*-
"""碧蓝航线小程序 UI 还原模板与资源。

模板与配色/布局尺寸均提取自 bilibili 碧蓝航线微信小程序 (wx3ee6dc49667f3444)
官方编译产物, 背景纹理为官方页面内嵌资源, 面板/标题/按钮图为官方 CDN 图。
"""
PAGE_BG = "data:image/png;base64,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"
NUM_STRIP = "data:image/png;base64,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"

TMPL_USER = """{# 碧蓝航线小程序「我的」页还原模板 (750rpx 设计稿 1:1) #}
<div class="bl-my">
  <img class="bl-my-top" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/my-top.png?885258fe" />

  {# ── 用户信息面板 my-box1 ── #}
  <div class="my-box1">
    <div class="bl-avtr" style="background-image:url('{{ avatar or default_avatar }}')"></div>
    <div class="bl-nickname">{{ nickname }}</div>
    <div class="bl-lv">{{ level }}</div>
    <div class="bl-server">{{ server_short }}</div>
    <div class="bl-uid">{{ uid }}</div>
    <div class="bl-teamname">{{ teamname }}</div>

    <div class="bl-num bl-num1 c-blue">{{ stats.collection_rate }}</div>
    <div class="bl-num bl-num2 c-blue">{{ stats.mainline_progress }}</div>
    <div class="bl-num bl-num3 c-blue"><span class="{{ 'c-blue' if stats.dorm_cur == 0 else 'c-pink' }}">{{ stats.dorm_cur }}</span>/{{ stats.dorm_max }}</div>
    <div class="bl-num bl-num4 c-blue"><span class="{{ 'c-blue' if stats.oil_cur < stats.oil_max else 'c-pink' }}">{{ stats.oil_cur }}</span>/{{ stats.oil_max }}</div>
    <div class="bl-num bl-num5 c-blue"><span class="{{ 'c-blue' if stats.coins_cur < stats.coins_max else 'c-pink' }}">{{ stats.coins_cur }}</span>/{{ stats.coins_max }}</div>
    <div class="bl-num bl-num6 c-blue"><span class="{{ 'c-pink' if stats.food_cur == 0 else 'c-blue' }}">{{ stats.food_cur }}</span>/{{ stats.food_max }}</div>
  </div>

  {# ── 委托/科研进度面板 my-box2 ── #}
  <div class="my-box2">
    <div class="bl-content1">
      <div class="content-num">
        <div class="bl-process">{{ commissions.completed }}</div>
        <div class="bl-process">{{ commissions.in_progress }}</div>
        <div class="bl-process">{{ commissions.idle }}</div>
      </div>
    </div>
    <div class="bl-content2">
      <div class="content-num">
        <div class="bl-process">{{ research.completed }}</div>
        <div class="bl-process">{{ research.in_progress }}</div>
        <div class="bl-process">{{ research.idle }}</div>
      </div>
    </div>
    {% if under_maintenance %}
    <img class="bl-delay-tip" src="{{ maintenance_img }}" />
    {% endif %}
  </div>

  {# ── 待办副本面板 my-box3 ── #}
  <div class="my-box3">
    <div class="one-tag">
      <img class="tag-pic" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/tag1.png?b4276e87" />
      <div class="tag-content add-bg">
        <div class="tag-title">当前信标 META挑战次数</div>
        <div class="tag-num"><span class="{{ 'c-blue' if beacon_meta.remain == 0 else 'c-pink' }}">{{ beacon_meta.remain }}</span>/{{ beacon_meta.max }}</div>
      </div>
      <div class="tag-content">
        <div class="tag-title">解析信标数量</div>
        <div class="tag-num"><span class="{{ 'c-blue' if beacon_parse.remain == 0 else 'c-pink' }}">{{ beacon_parse.remain }}</span>/{{ beacon_parse.max }}</div>
      </div>
    </div>

    <div class="one-tag">
      <img class="tag-pic" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/tag2.png?9179c490" />
      <div class="tag-content add-bg">
        <div class="tag-title">今日剩余次数</div>
        <div class="tag-num"><span class="{{ 'c-blue' if exercise.remain == 0 else 'c-pink' }}">{{ exercise.remain }}</span>/{{ exercise.max }}</div>
      </div>
    </div>

    <div class="one-tag">
      <img class="tag-pic" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/tag3.png?957e6bff" />
      <div class="tag-content add-bg">
        <div class="tag-title">主线困难关卡</div>
        <div class="tag-num"><span class="{{ 'c-blue' if hard_stage.remain == 0 else 'c-pink' }}">{{ hard_stage.remain }}</span>/{{ hard_stage.max }}</div>
      </div>
    </div>

    {% if dailies %}
    <div class="one-tag">
      <img class="tag-pic" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/tag4.png?fe3b9743" />
      {% for d in dailies %}
      <div class="tag-content {{ 'add-bg' if loop.index0 % 2 == 0 else '' }}">
        <div class="tag-title">{{ d.name }}</div>
        <div class="tag-num"><span class="{{ 'c-blue' if d.remain == 0 else 'c-pink' }}">{{ d.remain }}</span>/{{ d.total }}</div>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  </div>

  <div class="bl-footer">Generated by 碧蓝航线助手 · {{ generated }} · 数据: bilibili 小程序接口</div>
</div>

<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: url({{ page_bg }}) 50%/cover; background-repeat: repeat-y; }
  body { width: 750px; font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif; }
  .bl-my { width: 750px; padding-bottom: 24px; overflow: hidden; }
  .c-blue { color: #6bb9e1; }
  .c-pink { color: #ed86a4; }

  .bl-my-top { display: block; width: 737px; height: 125px; margin-left: 13px; object-fit: contain; }

  .my-box1 {
    position: relative; width: 725px; height: 409px; margin: -50px 0 0 25px;
    background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/my-box1.png?c79e751a);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
    color: #53baef; font-size: 28px; font-weight: 700;
  }
  .my-box1 .bl-avtr { position: absolute; left: 24px; top: 32px; width: 130px; height: 130px; border-radius: 50%; background-position: 50%; background-size: cover; }
  .my-box1 .bl-nickname { position: absolute; left: 240px; top: 24px; width: 240px; height: 40px; line-height: 40px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .my-box1 .bl-lv { position: absolute; left: 490px; top: 25px; height: 40px; line-height: 40px; }
  .my-box1 .bl-server { position: absolute; left: 500px; top: 24px; width: 200px; height: 40px; line-height: 40px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: right; }
  .my-box1 .bl-uid { position: absolute; left: 240px; top: 78px; height: 40px; line-height: 40px; }
  .my-box1 .bl-teamname { position: absolute; left: 335px; top: 130px; height: 40px; line-height: 40px; }
  .bl-num { position: absolute; width: 212px; height: 30px; line-height: 30px; text-align: center; }
  .my-box1 .bl-num1 { left: 34px; top: 200px; }
  .my-box1 .bl-num2 { left: 248px; top: 200px; }
  .my-box1 .bl-num3 { left: 460px; top: 200px; }
  .my-box1 .bl-num4 { left: 34px; top: 290px; }
  .my-box1 .bl-num5 { left: 248px; top: 290px; }
  .my-box1 .bl-num6 { left: 460px; top: 290px; }

  .my-box2 {
    position: relative; width: 715px; height: 596px; margin: 20px 0 0 18px; padding-top: 105px;
    background-image: url(https://i0.hdslb.com/bfs/game-static/80652cb84240c471636112b7a5fcfda664d7c756.png);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
  }
  .bl-content1, .bl-content2 {
    position: relative; width: 646px; height: 202px; margin: 0 auto 16px;
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
  }
  .bl-content1 { background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/content1.png?2aeaa739); }
  .bl-content2 { background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/content2.png?ae7a611e); }
  .content-num {
    position: absolute; left: 195px; top: 26px; width: 433px; height: 152px;
    background-image: url({{ num_strip }}); background-position: 50%; background-repeat: no-repeat; background-size: 100% 100%;
    color: #6bb9e1; font-size: 26px; font-weight: 700;
  }
  .bl-process { height: 44px; line-height: 44px; padding-right: 20px; text-align: right; }
  .bl-delay-tip { display: block; width: 346px; height: 24px; margin: 20px auto 0; }

  .my-box3 {
    position: relative; width: 716px; height: 843px; margin: 20px 0 0 18px; padding: 90px 26px 0;
    background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/my-box3.png?4fd40d5e);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
  }
  .one-tag { width: 646px; margin-top: 10px; padding-bottom: 15px; border-bottom: 2px solid #f4f4f4; }
  .one-tag:last-child { border-bottom: none; }
  .tag-pic { display: block; width: 171px; height: 43px; margin-left: 10px; }
  .tag-content { display: flex; align-items: center; width: 646px; height: 42px; padding: 0 10px; color: #6bb9e1; font-size: 28px; }
  .tag-content.add-bg { background: #f4f5f9; }
  .tag-title { height: 28px; line-height: 28px; padding-left: 20px; border-left: 5px solid #6bb9e1; }
  .tag-num { flex: 1; text-align: right; }

  .bl-footer { margin-top: 18px; text-align: center; font-size: 20px; color: #6bb9e1; opacity: .65; }
</style>
<script>
(function () {
  function fit() {
    var w = document.documentElement.clientWidth;
    if (w > 0 && w < 750) { document.body.style.zoom = w / 750; }
  }
  if (document.readyState === 'complete') { fit(); } else { window.addEventListener('load', fit); }
})();
</script>"""

TMPL_BUILD = """{# 碧蓝航线小程序「建造记录」页还原模板 (750rpx 设计稿 1:1) #}
<div class="bl-build">
  <img class="bl-my-top" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl-role/my-top.png?885258fe" />

  {# ── 玩家信息条 ── #}
  <div class="my-box1 login-after">
    <div class="bl-avtr" style="background-image:url('{{ avatar or default_avatar }}')"></div>
    <div class="bl-nickname">{{ nickname }}</div>
    <div class="bl-server">{{ server_short }}</div>
    <div class="bl-uid">{{ uid }}</div>
  </div>

  {# ── 建造记录列表 ── #}
  <div class="my-box2">
    <img class="build-title" src="https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl/build-title.png?962d27c5" />
    <div class="condition-show">
      <div class="condition-show-title">{{ summary }}</div>
      {% if page_total > 1 %}
      <div class="condition-page">{{ page_no }}/{{ page_total }}</div>
      {% endif %}
    </div>

    {% for r in records %}
    <div class="build-one">
      <div class="build-content-title">{{ r.taskName }}</div>
      <div class="build-content-time">{{ r.time }}</div>
      <div class="build-content-avtr" style="background-image:url('{{ r.avatarIcon or default_avatar }}')"></div>
      <div class="build-content-name">{{ r.name }}</div>
    </div>
    {% endfor %}

    <img class="build-tip" src="https://i0.hdslb.com/bfs/game-static/a0c23d5dae12fdf3140d5816341711abca932467.png" />
  </div>

  <div class="bl-footer">Generated by 碧蓝航线助手 · {{ generated }} · 数据: bilibili 小程序接口</div>
</div>

<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: url({{ page_bg }}) 50%/cover; background-repeat: repeat-y; }
  body { width: 750px; font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif; }
  .bl-build { width: 750px; padding-bottom: 24px; overflow: hidden; }

  .bl-my-top { display: block; width: 737px; height: 125px; margin-left: 13px; object-fit: contain; }

  .my-box1 {
    position: relative; width: 707px; height: 144px; margin: -50px 0 0 21.5px;
    color: #6bb9e1; font-size: 26px; font-weight: 700;
  }
  .my-box1.login-after {
    background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl/build-login-after.png?dd025be7);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
  }
  .my-box1 .bl-avtr { position: absolute; left: 36.5px; top: 21.5px; width: 100px; height: 100px; border-radius: 50%; background-position: 50%; background-size: cover; }
  .my-box1 .bl-nickname { position: absolute; left: 240px; top: 24px; width: 220px; height: 40px; line-height: 40px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .my-box1 .bl-server { position: absolute; left: 476px; top: 24px; width: 180px; height: 40px; line-height: 40px; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .my-box1 .bl-uid { position: absolute; left: 240px; top: 82px; height: 40px; line-height: 40px; }

  .my-box2 { width: 702px; height: auto; margin: 20px auto 0; padding: 20px 0 26px; background: #fff; border-radius: 8px; }
  .build-title { display: block; width: 646px; height: 65px; margin: 0 auto 5px; }
  .condition-show {
    display: flex; align-items: center; width: 646px; min-height: 64px; margin: 0 auto 16px; padding: 10px 18px;
    background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl/build-bg1.png?9cc56273);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
  }
  .condition-show-title { color: #6e96c2; font-size: 30px; font-weight: 700; line-height: 1.4; word-break: break-all; }
  .condition-page { margin-left: auto; color: #ed86a4; font-size: 26px; font-weight: 700; }

  .build-one {
    position: relative; width: 646px; height: 142px; margin: 0 auto 16px; padding: 26px 0 0 20px;
    background-image: url(https://s1.hdslb.com/bfs/static/game-static/totalMiniprogram/src/img/bl/build-one.png?45da8322);
    background-position: 50%; background-repeat: no-repeat; background-size: cover;
    color: #6e96c2; font-size: 24px;
  }
  .build-content-title { font-size: 30px; font-weight: 500; margin-bottom: 16px; }
  .build-content-avtr { position: absolute; right: 35px; top: 19px; width: 80px; height: 80px; border-radius: 50%; background-position: 50%; background-size: cover; }
  .build-content-name { position: absolute; right: 32px; top: 102px; width: 346px; text-align: right; }

  .build-tip { display: block; width: 555px; height: 96px; margin: 0 auto; }

  .bl-footer { margin-top: 18px; text-align: center; font-size: 20px; color: #6bb9e1; opacity: .65; }
</style>
<script>
(function () {
  function fit() {
    var w = document.documentElement.clientWidth;
    if (w > 0 && w < 750) { document.body.style.zoom = w / 750; }
  }
  if (document.readyState === 'complete') { fit(); } else { window.addEventListener('load', fit); }
})();
</script>"""
