// 训练计划编辑器
class TrainingPlanEditor {
  constructor() {
    this.currentDay = 0;
    this.currentPlanId = null; // 当前编辑的计划ID
    this.planData = this.initializePlanData();
    this.favoriteExercises = this.loadFavoriteExercises();
    this.draggedElement = null;
    this.draggedModule = null;
    this.draggedIndex = null;
    this.isDragging = false;
    this.init();
  }
  
  init() {
    try {
      this.applyUserWeights();
      this.renderWeekCards();
      this.renderExerciseLibrary();
      this.setupEventListeners();
      this.updateCurrentDayDisplay();
      this.setupButtonEventListeners();
      
      // 检查URL参数中是否有计划ID或导入标志
      const urlParams = new URLSearchParams(window.location.search);
      const planId = urlParams.get('plan_id');
      const importFlag = urlParams.get('import');
      
      if (planId) {
        this.loadPlan(planId);
      } else if (importFlag === 'true') {
        this.loadImportedPlan();
      } else {
        // 显示使用提示
        setTimeout(() => {
          this.showNotification('💡 提示：点击左侧周安排中的训练部位可直接编辑', 'info', 5000);
        }, 1000);
      }

    } catch (error) {
      console.error('训练计划编辑器初始化失败:', error);
    }
  }
  
  initializePlanData() {
    return {
      plan_name: "我的五分化计划",
      mode: "五分化",
      cycle_weeks: 8,
      week_schedule: this.getTemplateSchedule("五分化")
    };
  }

  // 获取训练模板
  getTemplateSchedule(mode) {
    const templates = {
      "五分化": [
        { weekday: "周一", body_parts: ["胸部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["背部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["肩部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["手臂"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "三分化": [
        { weekday: "周一", body_parts: ["胸部", "肩部", "三头肌"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["背部", "二头肌"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "推拉腿": [
        { weekday: "周一", body_parts: ["推"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["拉"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["腿"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "有氧运动": [
        { weekday: "周一", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["有氧"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "功能性训练": [
        { weekday: "周一", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["功能性"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ],
      "自定义": [
        { weekday: "周一", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周二", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周三", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周四", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周五", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周六", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
        { weekday: "周日", body_parts: ["自定义"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
      ]
    };
    
    return templates[mode] || templates["五分化"];
  }

  renderWeekCards() {
    const weekCardsContainer = document.getElementById('weekCards');
    if (!weekCardsContainer) return;
    
    weekCardsContainer.innerHTML = this.planData.week_schedule.map((day, index) => {
      const isActive = index === this.currentDay;
      const isRestDay = day.body_parts.includes('休息');
      const exerciseCount = Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
      
      return `
        <div class="week-card ${isActive ? 'active' : ''}" onclick="editor.handleWeekCardClick(event, ${index})">
          <div class="day-name">${day.weekday}</div>
          <div class="day-parts editable" 
               contenteditable="true" 
               data-day-index="${index}"
               onblur="editor.updateDayParts(${index}, this.textContent)"
               onkeydown="editor.handleDayPartsKeydown(event, ${index})"
               onclick="event.stopPropagation()"
               title="点击编辑训练部位">${day.body_parts.join(' + ')}</div>
          ${exerciseCount > 0 ? `<div class="exercise-count">${exerciseCount}个动作</div>` : ''}
        </div>
      `;
    }).join('');
    
    // 确保contenteditable属性正确设置
    setTimeout(() => {
      document.querySelectorAll('.day-parts.editable').forEach(element => {
        element.setAttribute('contenteditable', 'true');
      });
    }, 100);
    
    this.updatePlanStats();
  }

  // 更新训练部位
  updateDayParts(dayIndex, newText) {
    if (!this.planData.week_schedule[dayIndex]) return;
    
    // 清理和分割输入文本
    const parts = newText.trim()
      .split(/[+,，、\s]+/)
      .map(part => part.trim())
      .filter(part => part.length > 0);
    
    // 如果为空，设为休息
    if (parts.length === 0) {
      parts.push('休息');
    }
    
    // 更新数据
    this.planData.week_schedule[dayIndex].body_parts = parts;
    
    // 更新当前日标题（如果正在编辑当前选中的日）
    if (dayIndex === this.currentDay) {
      const currentDayTitle = document.getElementById('currentDayTitle');
      if (currentDayTitle) {
        const dayName = this.planData.week_schedule[dayIndex].weekday;
        const bodyParts = parts.join('、');
        currentDayTitle.textContent = `${dayName}：${bodyParts}`;
      }
    }
    
    // 重新渲染周卡片以反映更改
    this.renderWeekCards();
    
    // 显示保存提示
    this.showNotification('训练部位已更新', 'success');
  }

  // 处理训练部位编辑时的键盘事件
  handleDayPartsKeydown(event, dayIndex) {
    if (event.key === 'Enter') {
      event.preventDefault();
      event.target.blur(); // 触发onblur事件
    }
    
    // 阻止点击事件冒泡，避免切换日程
    event.stopPropagation();
  }

  // 处理周卡片点击事件
  handleWeekCardClick(event, dayIndex) {
    // 如果点击的是可编辑区域，不切换日程
    if (event.target.classList.contains('editable')) {
      return;
    }
    // 否则切换到对应的日程
    this.selectDay(dayIndex);
  }

  updatePlanStats() {
    let totalExercises = 0;
    let trainingDays = 0;
    let restDays = 0;
    let totalWeight = 0;
    
    this.planData.week_schedule.forEach(day => {
      const dayExercises = Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
      totalExercises += dayExercises;
      
      if (day.body_parts.includes('休息')) {
        restDays++;
      } else {
        trainingDays++;
      }
      
      // 计算总重量
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          if (exercise.weight && !isNaN(exercise.weight)) {
            totalWeight += parseFloat(exercise.weight) * parseInt(exercise.sets || 1);
          }
        });
      });
    });
    
    const elements = {
      totalExercises: document.getElementById('totalExercises'),
      trainingDays: document.getElementById('trainingDays'),
      restDays: document.getElementById('restDays'),
      totalWeight: document.getElementById('totalWeight')
    };
    
    if (elements.totalExercises) elements.totalExercises.textContent = totalExercises;
    if (elements.trainingDays) elements.trainingDays.textContent = trainingDays;
    if (elements.restDays) elements.restDays.textContent = restDays;
    if (elements.totalWeight) elements.totalWeight.textContent = `${totalWeight.toFixed(1)}kg`;
  }

  getTotalExercises() {
    let total = 0;
    this.planData.week_schedule.forEach(day => {
      total += Object.values(day.modules).reduce((sum, module) => sum + module.length, 0);
    });
    return total;
  }

  // 加载喜欢的动作
  loadFavoriteExercises() {
    const saved = localStorage.getItem('favorite_exercises');
    return saved ? JSON.parse(saved) : [];
  }

  // 保存喜欢的动作
  saveFavoriteExercises() {
    localStorage.setItem('favorite_exercises', JSON.stringify(this.favoriteExercises));
  }

  // 保存用户的重量设置
  saveUserWeights() {
    const userWeights = {};
    this.planData.week_schedule.forEach(day => {
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          if (exercise.weight !== undefined && exercise.weight !== '') {
            const exerciseName = typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作');
            userWeights[exerciseName] = exercise.weight;
          }
        });
      });
    });
    localStorage.setItem('user_exercise_weights', JSON.stringify(userWeights));
  }

  // 加载用户的重量设置
  loadUserWeights() {
    const saved = localStorage.getItem('user_exercise_weights');
    return saved ? JSON.parse(saved) : {};
  }

  // 应用用户的重量设置
  applyUserWeights() {
    const userWeights = this.loadUserWeights();
    this.planData.week_schedule.forEach(day => {
      Object.values(day.modules).forEach(module => {
        module.forEach(exercise => {
          const exerciseName = typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作');
          if (userWeights[exerciseName] && !exercise.weight) {
            exercise.weight = userWeights[exerciseName];
          }
        });
      });
    });
  }

  // 获取重量建议
  getWeightSuggestion(exerciseName, module) {
    const userWeights = this.loadUserWeights();
    const defaultWeight = this.getDefaultWeight(exerciseName, module);
    
    if (userWeights[exerciseName]) {
      return userWeights[exerciseName];
    }
    
    if (defaultWeight !== '') {
      return defaultWeight;
    }
    
    return '';
  }

  // 显示重量建议
  showWeightSuggestion(exerciseName, module) {
    const suggestion = this.getWeightSuggestion(exerciseName, module);
    if (suggestion) {
      this.showNotification(`建议重量: ${suggestion}kg`, 'info');
    }
  }

  // 添加喜欢的动作
  addFavoriteExercise(exerciseName) {
    const existingIndex = this.favoriteExercises.findIndex(fav => fav.name === exerciseName);
    if (existingIndex !== -1) {
      this.favoriteExercises[existingIndex].timestamp = Date.now();
    } else {
      this.favoriteExercises.push({
        name: exerciseName,
        timestamp: Date.now()
      });
    }
    this.saveFavoriteExercises();
    this.updateFavoriteButton(exerciseName, true);
    this.showNotification(`已添加"${exerciseName}"到喜欢列表`, 'success');
  }

  // 移除喜欢的动作
  removeFavoriteExercise(exerciseName) {
    this.favoriteExercises = this.favoriteExercises.filter(fav => fav.name !== exerciseName);
    this.saveFavoriteExercises();
    this.updateFavoriteButton(exerciseName, false);
    this.showNotification(`已从喜欢列表移除"${exerciseName}"`, 'info');
  }

  // 更新喜欢按钮状态
  updateFavoriteButton(exerciseName, isFavorite) {
    const buttons = document.querySelectorAll(`[data-exercise="${exerciseName}"] .favorite-btn`);
    buttons.forEach(btn => {
      if (isFavorite) {
        btn.classList.add('favorite-active');
        btn.title = '取消喜欢';
      } else {
        btn.classList.remove('favorite-active');
        btn.title = '添加到喜欢';
      }
    });
  }

  // 检查动作是否被喜欢
  isFavoriteExercise(exerciseName) {
    return this.favoriteExercises.some(fav => fav.name === exerciseName);
  }

  // 获取喜欢的动作
  getFavoriteExercises() {
    return this.favoriteExercises
      .sort((a, b) => b.timestamp - a.timestamp)
      .map(fav => fav.name);
  }

  // 渲染动作库
  renderExerciseLibrary() {
    const exerciseLibrary = document.querySelector('.exercise-library .body-parts');
    if (!exerciseLibrary) {
      // console.warn('找不到动作库容器');  // 调试信息已隐藏
      return;
    }

    const favoriteExercises = this.getFavoriteExercises();
    
    // 定义所有动作数据
    const allExercises = {
      chest: [
        "杠铃卧推", "哑铃卧推", "上斜哑铃推", "下斜哑铃推", "器械推胸",
        "绳索夹胸", "哑铃飞鸟", "上斜飞鸟", "下斜飞鸟", "窄距卧推",
        "史密斯卧推", "双杠臂屈伸(胸)", "蝴蝶机夹胸", "俯卧撑"
      ],
      back: [
        "引体向上", "杠铃划船", "高位下拉", "坐姿绳索划船", "哑铃划船",
        "T杠划船", "单臂哑铃划船", "直臂下拉", "反向飞鸟", "面拉",
        "俯身划船", "反手引体", "硬拉", "海豹划船"
      ],
      shoulders: [
        "坐姿哑铃推举", "杠铃推举", "哑铃侧平举", "哑铃前平举", "哑铃后束飞鸟",
        "耸肩", "绳索侧平举", "阿诺德推举", "面拉", "反向飞鸟",
        "推举机", "颈后推举", "俯身侧平举"
      ],
      legs: [
        "杠铃深蹲", "罗马尼亚硬拉", "腿举", "腿弯举", "小腿提踵",
        "前蹲", "腿外展", "腿内收", "保加利亚分腿蹲", "哑铃深蹲",
        "箭步蹲", "腿屈伸", "哈克深蹲", "臀桥", "硬拉"
      ],
      arms: [
        "杠铃弯举", "三头肌下拉", "哑铃弯举", "锤式弯举", "绳索下拉",
        "窄距卧推", "牧师椅弯举", "仰卧臂屈伸", "绳索弯举", "钻石俯卧撑",
        "集中弯举", "法式卧推", "绳索过顶臂屈伸"
      ],
      core: [
        "平板支撑", "俄罗斯转体", "卷腹", "仰卧举腿", "侧平板",
        "死虫式", "鸟狗式", "悬垂举腿", "仰卧两头起", "龙旗",
        "V字两头起", "反向卷腹", "触足卷腹"
      ],
      cardio: [
        "跑步", "椭圆机", "动感单车", "划船机", "跳绳", "HIIT", "爬楼机"
      ],
      functional: [
        "波比跳", "深蹲跳", "高抬腿", "开合跳", "俯卧撑",
        "单腿深蹲", "梯子训练", "锥桶训练", "药球投掷", "壶铃摆动",
        "推雪橇", "战绳", "农夫行走"
      ],
      stretch: [
        "动态拉伸", "静态拉伸", "胸部拉伸", "背部拉伸", "肩部拉伸",
        "腿部拉伸", "手臂拉伸", "髋部拉伸", "瑜伽", "泡沫轴放松",
        "腘绳肌拉伸", "股四头肌拉伸", "髋屈肌拉伸"
      ]
    };

    const partNames = {
      chest: "胸部",
      back: "背部", 
      shoulders: "肩部",
      legs: "腿部",
      arms: "手臂",
      core: "核心",
      cardio: "有氧",
      functional: "功能性",
      stretch: "拉伸"
    };

    let html = '';

    // 首先渲染喜欢的动作
    if (favoriteExercises.length > 0) {
      html += `
        <div class="part-category" data-part="favorites">
          <div class="part-header">
            <i class="fas fa-chevron-right"></i>
            <span><i class="fas fa-heart" style="color: #ff6b35;"></i> 我喜欢的</span>
          </div>
          <div class="part-exercises" style="display: none;">
      `;
      
      favoriteExercises.forEach(exerciseName => {
        html += `
          <div class="exercise-item" draggable="true" data-exercise="${exerciseName}">
            <span>${exerciseName}</span>
            <button class="favorite-btn favorite-active" onclick="editor.toggleFavorite('${exerciseName}')" title="取消喜欢">
              <i class="fas fa-heart"></i>
            </button>
          </div>
        `;
      });
      
      html += '</div></div>';
    }

    // 渲染各个部位的动作
    Object.keys(allExercises).forEach(part => {
      html += `
        <div class="part-category" data-part="${part}">
          <div class="part-header">
            <i class="fas fa-chevron-right"></i>
            <span>${partNames[part]}</span>
          </div>
          <div class="part-exercises" style="display: none;">
      `;
      
      allExercises[part].forEach(exerciseName => {
        const isFavorite = this.isFavoriteExercise(exerciseName);
        html += `
          <div class="exercise-item" draggable="true" data-exercise="${exerciseName}">
            <span>${exerciseName}</span>
            <button class="favorite-btn ${isFavorite ? 'favorite-active' : ''}" onclick="editor.toggleFavorite('${exerciseName}')" title="${isFavorite ? '取消喜欢' : '添加到喜欢'}">
              <i class="fas fa-heart"></i>
            </button>
          </div>
        `;
      });
      
      html += '</div></div>';
    });

    exerciseLibrary.innerHTML = html;
  }

  // 切换喜欢状态
  toggleFavorite(exerciseName) {
    if (this.isFavoriteExercise(exerciseName)) {
      this.removeFavoriteExercise(exerciseName);
    } else {
      this.addFavoriteExercise(exerciseName);
    }
  }

  selectDay(dayIndex) {
    this.currentDay = dayIndex;
    this.renderWeekCards();
    this.updateCurrentDayDisplay();
  }
  
  updateCurrentDayDisplay() {
    try {
      const currentDay = this.planData.week_schedule[this.currentDay];
      const titleElement = document.getElementById('currentDayTitle');
      if (titleElement) {
        titleElement.textContent = `${currentDay.weekday}：${currentDay.body_parts.join(' + ')}`;
      }
      this.renderAllModules();
    } catch (error) {
      console.error('更新当前天显示失败:', error);
    }
  }

  renderAllModules() {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const modules = ['warmup', 'main', 'accessory', 'cooldown'];
    
    modules.forEach(module => {
      this.renderModule(module, currentDay.modules[module]);
    });
  }
  
  setupEventListeners() {
    // 模式选择
    document.querySelectorAll('.mode-option').forEach(option => {
      option.addEventListener('click', (e) => {
        document.querySelectorAll('.mode-option').forEach(o => o.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.changeMode(e.currentTarget.dataset.mode);
      });
    });
    
    // 部位分类切换
    document.addEventListener('click', (e) => {
      if (e.target.closest('.part-header')) {
        const header = e.target.closest('.part-header');
        const category = header.closest('.part-category');
        if (category && category.dataset.part) {
          this.togglePartCategory(category.dataset.part);
        }
      }
    });
    
    // 拖拽功能
    this.setupDragAndDrop();
    
    // 模块切换
    document.querySelectorAll('.module-toggle').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const module = e.currentTarget.closest('.module-section');
        if (module) {
          this.toggleModule(module);
        }
      });
    });
  }
  
  setupButtonEventListeners() {
    // 使用事件委托，确保按钮点击事件能正常工作
    document.addEventListener('click', (e) => {
      if (e.target.closest('#weekSettingsBtn')) {
        e.preventDefault();
        e.stopPropagation();
        this.showWeekSettings();
        return false;
      }
    });
    
    // 也尝试直接绑定，以防事件委托不工作
    const bindButton = () => {
      const weekSettingsBtn = document.getElementById('weekSettingsBtn');
      if (weekSettingsBtn) {
        // 移除可能存在的旧事件监听器
        weekSettingsBtn.removeEventListener('click', this.handleWeekSettingsClick);
        
        // 添加新的事件监听器
        this.handleWeekSettingsClick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.showWeekSettings();
          return false;
        };
        
        weekSettingsBtn.addEventListener('click', this.handleWeekSettingsClick);

        return true;
      } else {
        // console.warn('未找到周安排按钮元素，将在100ms后重试');  // 调试信息已隐藏
        return false;
      }
    };
    
    // 立即尝试绑定
    if (!bindButton()) {
      // 如果立即绑定失败，延迟重试
      setTimeout(() => {
        if (!bindButton()) {
          setTimeout(bindButton, 500); // 再次重试
        }
      }, 100);
    }
  }
  
  showWeekSettings() {

    this.showNotification('周安排设置功能开发中...', 'info');
  }

  // 从API加载模板数据
  async loadTemplateFromAPI(templateName) {
    try {
      const response = await fetch('/tools/api/training_plans/templates/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // 处理API返回的数据结构
      if (data.success && data.templates) {
        let templates = data.templates;
        
        // 如果templates是对象，转换为数组
        if (typeof templates === 'object' && !Array.isArray(templates)) {
          templates = Object.keys(templates).map(key => ({
            id: key,
            ...templates[key]
          }));
        }
        
        // 根据模板名称查找对应的模板数据
        const template = templates.find(t => t.name === templateName || t.mode === templateName);
        if (template) {
          // 返回schedule数据，这里包含了完整的模块预设动作
          return template.schedule || template.week_schedule || [];
        }
      }

      return null;
    } catch (error) {
      console.error('加载模板失败:', error);
      return null;
    }
  }

  // 加载从训练计划器导入的计划
  loadImportedPlan() {
    try {
      const importedPlanData = localStorage.getItem('importedPlan');
      if (!importedPlanData) {
        this.showNotification('未找到导入的计划数据', 'error');
        return;
      }

      const planData = JSON.parse(importedPlanData);
      
      // 更新编辑器数据
      this.planData = planData;
      
      // 更新计划名称
      const planNameInput = document.getElementById('planName');
      if (planNameInput) {
        planNameInput.value = planData.plan_name;
      }
      
      // 重新渲染界面
      this.renderWeekCards();
      this.updateCurrentDayDisplay();
      this.renderAllModules();
      
      // 清除localStorage中的数据
      localStorage.removeItem('importedPlan');
      
      this.showNotification('成功导入训练计划！', 'success');
      
    } catch (error) {
      console.error('导入计划失败:', error);
      this.showNotification('导入计划失败，请重试', 'error');
    }
  }
  
  async changeMode(mode) {
    try {
      this.planData.mode = mode;
      
      // 从API获取模板数据
      const templateData = await this.loadTemplateFromAPI(mode);
      if (templateData) {
        this.planData.week_schedule = templateData;
        
        // 确保模板中的预设动作能够正确加载到exercise-drop-zone

      } else {
        // 如果API失败，使用本地模板
        this.planData.week_schedule = this.getTemplateSchedule(mode);
      }
      
      this.renderWeekCards();
      this.updateCurrentDayDisplay();
      this.renderAllModules();
      this.showNotification(`已切换到${mode}模式`, 'success');
    } catch (error) {
      console.error('切换模式失败:', error);
      // 回退到本地模板
      this.planData.mode = mode;
      this.planData.week_schedule = this.getTemplateSchedule(mode);
      this.renderWeekCards();
      this.updateCurrentDayDisplay();
      this.renderAllModules();
      this.showNotification(`已切换到${mode}模式`, 'success');
    }
  }
  
  togglePartCategory(part) {
    const category = document.querySelector(`[data-part="${part}"]`);
    const exercises = category.querySelector('.part-exercises');
    const icon = category.querySelector('.part-header i');
    
    if (exercises.style.display === 'none') {
      exercises.style.display = 'block';
      icon.className = 'fas fa-chevron-down';
      category.classList.add('active');
    } else {
      exercises.style.display = 'none';
      icon.className = 'fas fa-chevron-right';
      category.classList.remove('active');
    }
  }
  
  setupDragAndDrop() {
    // 动作拖拽
    document.addEventListener('dragstart', (e) => {
      if (e.target.closest('.exercise-item')) {
        const item = e.target.closest('.exercise-item');
        e.dataTransfer.setData('text/plain', item.dataset.exercise);
        item.style.opacity = '0.5';
      }
    });
    
    document.addEventListener('dragend', (e) => {
      if (e.target.closest('.exercise-item')) {
        const item = e.target.closest('.exercise-item');
        item.style.opacity = '1';
      }
    });
    
    // 放置区域
    document.querySelectorAll('.exercise-drop-zone').forEach(zone => {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
      });
      
      zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
      });
      
      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        
        const exerciseName = e.dataTransfer.getData('text/plain');
        const module = zone.dataset.module;
        this.addExercise(exerciseName, module);
      });
    });
  }
  
  addExercise(exerciseName, module) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = {
      name: exerciseName,
      sets: this.getDefaultSets(exerciseName, module),
      weight: this.getDefaultWeight(exerciseName, module),
      reps: this.getDefaultReps(exerciseName, module),
      rest: this.getDefaultRest(exerciseName, module)
    };
    
    currentDay.modules[module].push(exercise);
    this.renderModule(module, currentDay.modules[module]);
    this.renderWeekCards();
    this.showNotification(`已添加"${exerciseName}"到${this.getModuleName(module)}模块`, 'success');
  }

  // 获取动作的默认参数
  getDefaultSets(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '1';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '1';
    }
    if (functionalExercises.includes(exerciseName)) {
      return '3';
    }
    if (module === 'warmup') {
      return '2';
    }
    if (module === 'main') {
      return '4';
    }
    return '3';
  }

  getDefaultReps(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '10分钟';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '20-30分钟';
    }
    if (coreExercises.includes(exerciseName)) {
      return '60秒';
    }
    if (functionalExercises.includes(exerciseName)) {
      if (exerciseName === '波比跳') return '10次';
      if (exerciseName === '深蹲跳') return '15次';
      if (exerciseName === '高抬腿' || exerciseName === '开合跳') return '30秒';
      if (exerciseName === '梯子训练') return '5分钟';
      if (exerciseName === '锥桶训练') return '8分钟';
      return '20次';
    }
    if (module === 'warmup') {
      return '15-20';
    }
    if (module === 'main') {
      return '8-10';
    }
    return '10-12';
  }

  getDefaultWeight(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    const bodyweightExercises = ['引体向上', '俯卧撑', '双杠臂屈伸', '深蹲', '单腿深蹲', '保加利亚分腿蹲'];
    
    // 不需要重量的动作
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '';
    }
    if (coreExercises.includes(exerciseName)) {
      return '';
    }
    if (functionalExercises.includes(exerciseName)) {
      return '';
    }
    if (bodyweightExercises.includes(exerciseName)) {
      return '';
    }
    
    // 根据动作类型设置默认重量
    const weightMap = {
      // 胸部动作
      '杠铃卧推': 60, '哑铃卧推': 20, '上斜哑铃推': 18, '下斜哑铃推': 18, '器械推胸': 50,
      '绳索夹胸': 15, '哑铃飞鸟': 12, '上斜飞鸟': 10, '下斜飞鸟': 10, '窄距卧推': 50,
      
      // 背部动作
      '杠铃划船': 40, '高位下拉': 45, '坐姿绳索划船': 35, '哑铃划船': 15, 'T杠划船': 30,
      '单臂哑铃划船': 12, '直臂下拉': 20, '反向飞鸟': 8, '面拉': 12,
      
      // 肩部动作
      '坐姿哑铃推举': 16, '杠铃推举': 40, '哑铃侧平举': 8, '哑铃前平举': 8, '哑铃后束飞鸟': 6,
      '耸肩': 20, '绳索侧平举': 8, '阿诺德推举': 14,
      
      // 腿部动作
      '杠铃深蹲': 80, '罗马尼亚硬拉': 70, '腿举': 100, '腿弯举': 30, '小腿提踵': 40,
      '前蹲': 60, '腿外展': 25, '腿内收': 25, '保加利亚分腿蹲': 12, '哑铃深蹲': 15,
      
      // 手臂动作
      '杠铃弯举': 20, '三头肌下拉': 25, '哑铃弯举': 8, '锤式弯举': 8, '绳索下拉': 20,
      '窄距卧推': 40, '牧师椅弯举': 15, '仰卧臂屈伸': 12, '绳索弯举': 15, '钻石俯卧撑': '',
      
      // 有氧和功能性动作
      'HIIT': '', '跳绳': '', '波比跳': '', '深蹲跳': '', '高抬腿': '', '开合跳': '',
      '梯子训练': '', '锥桶训练': '', '药球投掷': 8, '壶铃摆动': 16
    };
    
    return weightMap[exerciseName] || '';
  }

  getDefaultRest(exerciseName, module) {
    const warmupExercises = ['动态拉伸', '静态拉伸', '胸部拉伸', '背部拉伸', '肩部拉伸', '腿部拉伸', '手臂拉伸', '髋部拉伸'];
    const cardioExercises = ['跑步', '椭圆机', '动感单车', '划船机', '跳绳', 'HIIT'];
    const coreExercises = ['平板支撑', '侧平板', '死虫式', '鸟狗式'];
    const functionalExercises = ['波比跳', '深蹲跳', '高抬腿', '开合跳', '梯子训练', '锥桶训练'];
    
    if (warmupExercises.includes(exerciseName) || module === 'cooldown') {
      return '无';
    }
    if (cardioExercises.includes(exerciseName)) {
      return '无';
    }
    if (coreExercises.includes(exerciseName)) {
      return '60秒';
    }
    if (functionalExercises.includes(exerciseName)) {
      if (exerciseName === '波比跳' || exerciseName === '深蹲跳') return '90秒';
      if (exerciseName === '高抬腿' || exerciseName === '开合跳') return '60秒';
      if (exerciseName === '梯子训练' || exerciseName === '锥桶训练') return '90秒';
      return '60秒';
    }
    if (module === 'warmup') {
      return '30秒';
    }
    if (module === 'main') {
      return '3分钟';
    }
    return '90秒';
  }
  
  getModuleName(module) {
    const names = {
      warmup: '热身', main: '主训', accessory: '辅助', cooldown: '拉伸'
    };
    return names[module] || module;
  }
  
  renderModule(module, exercises) {
    const dropZone = document.querySelector(`[data-module="${module}"] .exercise-drop-zone`);
    if (!dropZone) {
      // console.warn(`找不到模块 ${module} 的放置区域`);  // 调试信息已隐藏
      return;
    }

    if (exercises.length === 0) {
      dropZone.innerHTML = `
        <i class="fas fa-plus"></i>
        <p>拖拽${this.getModuleName(module)}动作至此</p>
      `;
    } else {
      // 先清空旧内容
      dropZone.innerHTML = '';
      
      // 重新生成每个动作卡片
      exercises.forEach((exercise, index) => {
        const cardHTML = this.createExerciseCard(exercise, module, index);

        dropZone.insertAdjacentHTML('beforeend', cardHTML);
      });
    }
  }

  createExerciseCard(exercise, module, index) {
    return `
      <div class="exercise-card" data-module="${module}" data-index="${index}" draggable="true" style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        cursor: move;
      " onmouseover="this.style.borderColor='rgba(255, 107, 53, 0.4)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(255, 107, 53, 0.15)';"
         onmouseout="this.style.borderColor='rgba(255, 107, 53, 0.2)'; this.style.transform='translateY(0)'; this.style.boxShadow='none';"
         ondragstart="editor.handleDragStart(event)"
         ondragover="editor.handleDragOver(event)"
         ondrop="editor.handleDrop(event)"
         ondragend="editor.handleDragEnd(event)">
        <div class="exercise-card-header" style="
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        ">
          <div class="exercise-card-name" style="
            font-weight: 600;
            color: #ff6b35;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
          ">
            <i class="fas fa-grip-vertical" style="font-size: 0.8rem; color: #a8a8a8; margin-right: 4px;" title="拖拽排序"></i>
            <i class="fas fa-dumbbell" style="font-size: 0.9rem;"></i>
            ${typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作')}
          </div>
          <div class="exercise-card-controls">
            <button class="card-control-btn" onclick="event.stopPropagation(); editor.removeExercise('${module}', ${index})" title="删除" style="
              background: rgba(255, 107, 53, 0.1);
              border: 1px solid rgba(255, 107, 53, 0.3);
              color: #ff6b35;
              padding: 6px 8px;
              border-radius: 6px;
              cursor: pointer;
              transition: all 0.3s ease;
              font-size: 0.8rem;
            " onmouseover="this.style.background='rgba(255, 107, 53, 0.2)'; this.style.transform='scale(1.05)';"
               onmouseout="this.style.background='rgba(255, 107, 53, 0.1)'; this.style.transform='scale(1)';">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="exercise-params" style="
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        ">
          <div class="param-group">
            <div class="param-label" style="
              font-size: 0.8rem;
              color: #ff6b35;
              font-weight: 600;
              margin-bottom: 6px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            ">组数</div>
            <input type="text" class="param-input" value="${exercise.sets}" 
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'sets', this.value)"
                   style="
                     width: 100%;
                     padding: 10px 12px;
                     border: 2px solid rgba(255, 255, 255, 0.1);
                     border-radius: 8px;
                     background: rgba(255, 255, 255, 0.05);
                     color: #e6e6e6;
                     font-size: 14px;
                     transition: all 0.3s ease;
                     box-sizing: border-box;
                   "
                   onfocus="this.style.borderColor='#ff6b35'; this.style.background='rgba(255, 255, 255, 0.1)'; this.style.boxShadow='0 0 0 3px rgba(255, 107, 53, 0.1)';"
                   onblur="this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.background='rgba(255, 255, 255, 0.05)'; this.style.boxShadow='none';">
          </div>
          <div class="param-group">
            <div class="param-label" style="
              font-size: 0.8rem;
              color: #ff6b35;
              font-weight: 600;
              margin-bottom: 6px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            ">重量(kg)</div>
            <input type="text" class="param-input" value="${exercise.weight || ''}" 
                   placeholder="重量或空杆"
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'weight', this.value)"
                   style="
                     width: 100%;
                     padding: 10px 12px;
                     border: 2px solid rgba(255, 255, 255, 0.1);
                     border-radius: 8px;
                     background: rgba(255, 255, 255, 0.05);
                     color: #e6e6e6;
                     font-size: 14px;
                     transition: all 0.3s ease;
                     box-sizing: border-box;
                   "
                   onfocus="this.style.borderColor='#ff6b35'; this.style.background='rgba(255, 255, 255, 0.1)'; this.style.boxShadow='0 0 0 3px rgba(255, 107, 53, 0.1)';"
                   onblur="this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.background='rgba(255, 255, 255, 0.05)'; this.style.boxShadow='none';">
          </div>
          <div class="param-group">
            <div class="param-label" style="
              font-size: 0.8rem;
              color: #ff6b35;
              font-weight: 600;
              margin-bottom: 6px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            ">次数</div>
            <input type="text" class="param-input" value="${exercise.reps}"
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'reps', this.value)"
                   style="
                     width: 100%;
                     padding: 10px 12px;
                     border: 2px solid rgba(255, 255, 255, 0.1);
                     border-radius: 8px;
                     background: rgba(255, 255, 255, 0.05);
                     color: #e6e6e6;
                     font-size: 14px;
                     transition: all 0.3s ease;
                     box-sizing: border-box;
                   "
                   onfocus="this.style.borderColor='#ff6b35'; this.style.background='rgba(255, 255, 255, 0.1)'; this.style.boxShadow='0 0 0 3px rgba(255, 107, 53, 0.1)';"
                   onblur="this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.background='rgba(255, 255, 255, 0.05)'; this.style.boxShadow='none';">
          </div>
          <div class="param-group">
            <div class="param-label" style="
              font-size: 0.8rem;
              color: #ff6b35;
              font-weight: 600;
              margin-bottom: 6px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            ">休息</div>
            <input type="text" class="param-input" value="${exercise.rest}"
                   onchange="editor.updateExerciseParam('${module}', ${index}, 'rest', this.value)"
                   style="
                     width: 100%;
                     padding: 10px 12px;
                     border: 2px solid rgba(255, 255, 255, 0.1);
                     border-radius: 8px;
                     background: rgba(255, 255, 255, 0.05);
                     color: #e6e6e6;
                     font-size: 14px;
                     transition: all 0.3s ease;
                     box-sizing: border-box;
                   "
                   onfocus="this.style.borderColor='#ff6b35'; this.style.background='rgba(255, 255, 255, 0.1)'; this.style.boxShadow='0 0 0 3px rgba(255, 107, 53, 0.1)';"
                   onblur="this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.background='rgba(255, 255, 255, 0.05)'; this.style.boxShadow='none';">
          </div>
        </div>
      </div>
    `;
  }

  removeExercise(module, index) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = currentDay.modules[module][index];
    currentDay.modules[module].splice(index, 1);
    this.renderModule(module, currentDay.modules[module]);
    this.renderWeekCards();
    const exerciseName = typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作');
    this.showNotification(`已删除"${exerciseName}"`, 'info');
  }

  updateExerciseParam(module, index, param, value) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    currentDay.modules[module][index][param] = value;
    
    // 如果是更新重量，保存用户设置
    if (param === 'weight') {
      this.saveUserWeights();
    }
  }

  quickAdjustWeight(module, index, adjustment) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercise = currentDay.modules[module][index];
    const currentWeight = parseFloat(exercise.weight) || 0;
    const newWeight = Math.max(0, currentWeight + adjustment);
    exercise.weight = newWeight.toString();
    
    // 重新渲染模块以更新显示
    this.renderModule(module, currentDay.modules[module]);
    this.saveUserWeights();
    
    this.showNotification(`重量已调整为 ${newWeight}kg`, 'info');
  }
  
  toggleModule(module) {
    const content = module.querySelector('.module-content');
    const toggle = module.querySelector('.module-toggle');
    
    if (content.style.display === 'none') {
      content.style.display = 'block';
      toggle.classList.remove('collapsed');
    } else {
      content.style.display = 'none';
      toggle.classList.add('collapsed');
    }
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      <span>${message}</span>
    `;
    
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '12px 20px',
      borderRadius: '6px',
      color: 'white',
      fontSize: '14px',
      fontWeight: '500',
      zIndex: '10000',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      minWidth: '250px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      backgroundColor: type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3',
      animation: 'slideInRight 0.3s ease-out'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-in';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }

  // 加载训练计划
  loadPlan(planId) {
    if (!planId) return;
    
    this.showNotification('正在加载训练计划...', 'info');
    
    fetch(`/tools/api/training_plans/${planId}/`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        if (data && data.success) {
          this.loadPlanFromData(data.plan);
          this.showNotification('训练计划加载成功！', 'success');
        } else {
          throw new Error(data.error || '加载失败');
        }
      })
      .catch(error => {
        console.error('加载失败:', error);
        this.showNotification(`加载失败：${error.message}`, 'error');
      });
  }

  // 从数据加载训练计划
  loadPlanFromData(planData) {
    this.currentPlanId = planData.id;
    
    // 更新计划基本信息
    const planNameInput = document.getElementById('planName');
    const cycleWeeksSelect = document.getElementById('cycleWeeks');
    
    if (planNameInput) planNameInput.value = planData.name;
    if (cycleWeeksSelect) cycleWeeksSelect.value = planData.cycle_weeks;
    
    // 更新模式选择器
    document.querySelectorAll('.mode-option').forEach(option => {
      option.classList.remove('active');
      if (option.dataset.mode === planData.mode) {
        option.classList.add('active');
      }
    });
    
    // 转换训练计划数据格式
    this.planData = {
      plan_name: planData.name,
      mode: planData.mode,
      cycle_weeks: planData.cycle_weeks,
      week_schedule: this.convertServerDataToEditorFormat(planData.week_schedule)
    };
    
    // 重新渲染界面
    this.renderWeekCards();
    this.updateCurrentDayDisplay();
    this.renderAllModules();
  }

  // 转换服务器数据格式为编辑器格式
  convertServerDataToEditorFormat(serverSchedule) {
    // 如果服务器数据已经是新格式（包含modules字段），直接使用
    if (serverSchedule && serverSchedule.length > 0 && serverSchedule[0].modules) {
      return serverSchedule;
    }
    
    // 否则，初始化一周7天的数据结构并转换旧格式
    const weekDays = [
      { weekday: "周一", body_parts: ["胸部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周二", body_parts: ["背部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周三", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周四", body_parts: ["肩部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周五", body_parts: ["腿部"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周六", body_parts: ["手臂"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } },
      { weekday: "周日", body_parts: ["休息"], modules: { warmup: [], main: [], accessory: [], cooldown: [] } }
    ];
    
    // 填充服务器数据（旧格式）
    serverSchedule.forEach(dayData => {
      const dayIndex = dayData.day - 1;
      if (dayIndex >= 0 && dayIndex < 7) {
        weekDays[dayIndex].body_parts = dayData.type ? dayData.type.split(',') : ['自定义'];
        
        // 清空现有模块
        Object.keys(weekDays[dayIndex].modules).forEach(module => {
          weekDays[dayIndex].modules[module] = [];
        });
        
        // 添加动作到对应模块
        if (dayData.exercises && Array.isArray(dayData.exercises)) {
          dayData.exercises.forEach(exercise => {
            const module = exercise.module || 'main';
            weekDays[dayIndex].modules[module].push({
              name: typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作'),
              sets: exercise.sets?.toString() || '3',
              reps: exercise.reps || '10-12',
              weight: exercise.weight || '',
              rest: exercise.rest || '90秒'
            });
          });
        }
      }
    });
    
    return weekDays;
  }

  // 复制训练日
  copyDay(sourceDay, targetDay) {
    if (sourceDay < 0 || sourceDay >= this.planData.week_schedule.length ||
        targetDay < 0 || targetDay >= this.planData.week_schedule.length) {
      this.showNotification('无效的日期索引', 'error');
      return;
    }
    
    // 深拷贝源日期的训练内容
    const sourceData = this.planData.week_schedule[sourceDay];
    const targetData = this.planData.week_schedule[targetDay];
    
    // 复制模块内容，但保留目标日期的基本信息
    targetData.modules = JSON.parse(JSON.stringify(sourceData.modules));
    
    // 重新渲染当前显示的内容
    this.renderCurrentDay();
    this.updateStats();
    
    const sourceName = sourceData.weekday;
    const targetName = targetData.weekday;
    this.showNotification(`已将 ${sourceName} 的训练内容复制到 ${targetName}`, 'success');
  }
  
  // 导出训练计划为JSON
  exportPlanAsJSON() {
    const planName = document.getElementById('planName').value.trim() || '未命名计划';
    const cycleWeeks = document.getElementById('cycleWeeks').value;
    
    const exportData = {
      name: planName,
      mode: this.planData.mode,
      cycle_weeks: parseInt(cycleWeeks),
      week_schedule: this.planData.week_schedule,
      export_time: new Date().toISOString(),
      version: '1.0'
    };
    
    // 创建下载链接
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${planName}_训练计划.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    this.showNotification(`训练计划 "${planName}" 已导出为JSON文件`, 'success');
  }
  
  // 从JSON导入训练计划
  importPlanFromJSON(jsonData) {
    try {
      let planData;
      if (typeof jsonData === 'string') {
        planData = JSON.parse(jsonData);
      } else {
        planData = jsonData;
      }
      
      // 验证数据格式
      if (!planData.name || !planData.week_schedule) {
        throw new Error('无效的训练计划格式');
      }
      
      // 更新计划数据
      this.planData.mode = planData.mode || '自定义';
      this.planData.week_schedule = planData.week_schedule;
      
      // 更新UI
      document.getElementById('planName').value = planData.name;
      document.getElementById('cycleWeeks').value = planData.cycle_weeks || 8;
      
      // 重新渲染
      this.renderWeekCards();
      this.renderCurrentDay();
      this.updateStats();
      
      this.showNotification(`已导入训练计划 "${planData.name}"`, 'success');
    } catch (error) {
      console.error('导入失败:', error);
      this.showNotification(`导入失败: ${error.message}`, 'error');
    }
  }

  // 生成预览HTML
  generatePreviewHTML() {
    const planName = document.getElementById('planName').value.trim() || '未命名计划';
    const cycleWeeks = document.getElementById('cycleWeeks').value;
    
    let previewHTML = `
      <!DOCTYPE html>
      <html lang="zh-CN">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>训练计划预览 - ${planName}</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
          }
          .preview-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          }
          .plan-header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #ff6b35;
            padding-bottom: 20px;
          }
          .plan-title {
            font-size: 2rem;
            color: #ff6b35;
            margin-bottom: 10px;
          }
          .plan-meta {
            color: #666;
            font-size: 1.1rem;
          }
          .day-section {
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
          }
          .day-header {
            background: #ff6b35;
            color: white;
            padding: 15px 20px;
            font-size: 1.2rem;
            font-weight: bold;
          }
          .day-content {
            padding: 20px;
          }
          .module-section {
            margin-bottom: 20px;
          }
          .module-title {
            font-size: 1.1rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-left: 4px solid #ff6b35;
          }
          .exercise-list {
            margin-left: 20px;
          }
          .exercise-item {
            margin-bottom: 8px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
          }
          .exercise-name {
            font-weight: 500;
            color: #333;
          }
          .exercise-params {
            color: #666;
            font-size: 0.9rem;
            margin-top: 4px;
          }
          .no-exercises {
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 20px;
          }
          .print-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff6b35;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
          }
          @media print {
            .print-btn { display: none; }
            body { background: white; }
            .preview-container { box-shadow: none; }
          }
        </style>
      </head>
      <body>
        <button class="print-btn" onclick="window.print()">打印计划</button>
        <div class="preview-container">
          <div class="plan-header">
            <h1 class="plan-title">${planName}</h1>
            <div class="plan-meta">
              训练模式：${this.planData.mode} | 计划周期：${cycleWeeks}周
            </div>
          </div>
    `;
    
    // 生成每天的训练内容
    this.planData.week_schedule.forEach((day, index) => {
      const hasExercises = Object.values(day.modules).some(module => module.length > 0);
      
      previewHTML += `
        <div class="day-section">
          <div class="day-header">
            ${day.weekday} - ${day.body_parts.join(' + ')}
          </div>
          <div class="day-content">
      `;
      
      if (hasExercises) {
        const moduleNames = {
          warmup: '热身',
          main: '主训练',
          accessory: '辅助训练',
          cooldown: '拉伸放松'
        };
        
        Object.entries(day.modules).forEach(([moduleKey, exercises]) => {
          if (exercises.length > 0) {
            previewHTML += `
              <div class="module-section">
                <div class="module-title">${moduleNames[moduleKey] || moduleKey}</div>
                <div class="exercise-list">
            `;
            
            exercises.forEach(exercise => {
              previewHTML += `
                <div class="exercise-item">
                  <div class="exercise-name">${typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作')}</div>
                  <div class="exercise-params">
                    ${exercise.sets ? `${exercise.sets}组` : ''}
                    ${exercise.reps ? ` × ${exercise.reps}次` : ''}
                    ${exercise.weight ? ` @ ${exercise.weight}kg` : ''}
                    ${exercise.rest ? ` (休息${exercise.rest})` : ''}
                  </div>
                </div>
              `;
            });
            
            previewHTML += `
                </div>
              </div>
            `;
          }
        });
      } else {
        previewHTML += `
          <div class="no-exercises">
            ${day.body_parts.includes('休息') ? '今天是休息日，好好恢复吧！' : '暂未安排训练内容'}
          </div>
        `;
      }
      
      previewHTML += `
          </div>
        </div>
      `;
    });
    
    previewHTML += `
        </div>
      </body>
      </html>
    `;
    
    return previewHTML;
  }

  // 拖拽处理方法
  handleDragStart(event) {
    this.isDragging = true;
    this.draggedElement = event.target.closest('.exercise-card');
    this.draggedModule = this.draggedElement.dataset.module;
    this.draggedIndex = parseInt(this.draggedElement.dataset.index);

    // 设置拖拽效果
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', this.draggedElement.outerHTML);
    
    // 添加拖拽时的视觉效果
    this.draggedElement.style.opacity = '0.5';
    this.draggedElement.style.transform = 'rotate(3deg)';
  }

  handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    
    const targetCard = event.target.closest('.exercise-card');
    if (targetCard && targetCard !== this.draggedElement) {
      // 添加拖拽悬停效果
      targetCard.style.borderColor = 'rgba(255, 107, 53, 0.8)';
      targetCard.style.transform = 'translateY(-1px)';
    }
  }

  handleDrop(event) {
    event.preventDefault();
    
    const targetCard = event.target.closest('.exercise-card');
    if (targetCard && targetCard !== this.draggedElement && this.draggedElement) {
      const targetModule = targetCard.dataset.module;
      const targetIndex = parseInt(targetCard.dataset.index);
      
      // 只在同一个模块内进行排序
      if (targetModule === this.draggedModule) {
        this.reorderExercises(this.draggedModule, this.draggedIndex, targetIndex);
      }
      
      // 重置目标卡片样式
      targetCard.style.borderColor = 'rgba(255, 107, 53, 0.2)';
      targetCard.style.transform = 'translateY(0)';
    }
  }

  handleDragEnd(event) {

    // 重置拖拽元素样式
    if (this.draggedElement) {
      this.draggedElement.style.opacity = '1';
      this.draggedElement.style.transform = 'translateY(0)';
    }
    
    // 清除所有拖拽状态
    this.draggedElement = null;
    this.draggedModule = null;
    this.draggedIndex = null;
    this.isDragging = false;
    
    // 清除所有卡片的悬停效果
    document.querySelectorAll('.exercise-card').forEach(card => {
      card.style.borderColor = 'rgba(255, 107, 53, 0.2)';
      card.style.transform = 'translateY(0)';
    });
  }

  reorderExercises(module, fromIndex, toIndex) {
    const currentDay = this.planData.week_schedule[this.currentDay];
    const exercises = currentDay.modules[module];

    // 确保索引有效
    if (fromIndex < 0 || fromIndex >= exercises.length || toIndex < 0 || toIndex >= exercises.length) {
      // console.warn('无效的拖拽索引:', fromIndex, toIndex, 'exercises.length:', exercises.length);  // 调试信息已隐藏
      return;
    }
    
    // 如果是同一个位置，不需要移动
    if (fromIndex === toIndex) {

      return;
    }
    
    // 创建数组的深度拷贝进行操作
    const exercisesCopy = exercises.map(ex => ({...ex}));
    const movedExercise = exercisesCopy.splice(fromIndex, 1)[0];

    if (movedExercise) {
      exercisesCopy.splice(toIndex, 0, movedExercise);

      // 更新原始数据
      currentDay.modules[module] = exercisesCopy;
      
      // 重新渲染模块
      this.renderModule(module, exercisesCopy);
      
      // 显示通知
      this.showNotification(`已调整"${movedExercise.name}"的顺序`, 'success');
    }
  }
}

// 全局函数
function goBack() {
  window.history.back();
}

function loadTemplate() {
  document.getElementById('templateModal').style.display = 'flex';
}

function importPlan() {
  // 显示导入计划模态框
  showImportPlanModal();
}

function showImportPlanModal() {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.id = 'importPlanModal';
  
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3><i class="fas fa-download"></i> 导入训练计划</h3>
        <button class="modal-close" onclick="closeImportPlanModal()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div class="import-loading" id="importLoading">
          <i class="fas fa-spinner fa-spin"></i> 正在加载计划库...
        </div>
        <div class="plan-list" id="importPlanList" style="display: none;">
          <!-- 计划列表将在这里显示 -->
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // 加载用户的训练计划
  loadUserPlansForImport();
}

function closeImportPlanModal() {
  const modal = document.getElementById('importPlanModal');
  if (modal) {
    modal.remove();
  }
}

async function loadUserPlansForImport() {
  try {
    const response = await fetch('/tools/api/training_plans/list/');
    const data = await response.json();
    
    const loadingEl = document.getElementById('importLoading');
    const listEl = document.getElementById('importPlanList');
    
    if (data.success && data.plans && data.plans.length > 0) {
      loadingEl.style.display = 'none';
      listEl.style.display = 'block';
      
      listEl.innerHTML = data.plans.map(plan => `
        <div class="import-plan-item">
          <div class="plan-info">
            <h4>${plan.name}</h4>
            <div class="plan-details">
              <span><i class="fas fa-dumbbell"></i> ${plan.mode}</span>
              <span><i class="fas fa-calendar"></i> ${plan.cycle_weeks}周</span>
              <span><i class="fas fa-clock"></i> ${new Date(plan.updated_at).toLocaleDateString()}</span>
              ${plan.is_active ? '<span class="active-badge"><i class="fas fa-check-circle"></i> 激活中</span>' : ''}
            </div>
          </div>
          <button class="import-btn" onclick="importSelectedPlan(${plan.id}, '${plan.name}')">
            <i class="fas fa-download"></i> 导入
          </button>
        </div>
      `).join('');
    } else {
      loadingEl.innerHTML = `
        <div class="no-plans">
          <i class="fas fa-folder-open" style="font-size: 3rem; color: #ccc; margin-bottom: 15px;"></i>
          <p>还没有保存的训练计划</p>
          <small>先在编辑器中创建并保存一个计划吧！</small>
        </div>
      `;
    }
  } catch (error) {
    console.error('加载计划失败:', error);
    const loadingEl = document.getElementById('importLoading');
    loadingEl.innerHTML = `
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <p>加载失败，请重试</p>
      </div>
    `;
  }
}

async function importSelectedPlan(planId, planName) {
  if (!confirm(`确定要导入训练计划"${planName}"吗？这将替换当前编辑器中的内容。`)) {
    return;
  }
  
  try {
    if (editor) {
      editor.showNotification('正在导入训练计划...', 'info');
      editor.loadPlan(planId);
      closeImportPlanModal();
    }
  } catch (error) {
    console.error('导入失败:', error);
    alert('导入失败，请重试');
  }
}

// 复制训练日功能
function copyDay() {
  if (!editor) {
    alert('编辑器未初始化');
    return;
  }
  
  const sourceDay = prompt('请输入要复制的源日期 (1-7):', '1');
  const targetDay = prompt('请输入要复制到的目标日期 (1-7):', '2');
  
  if (sourceDay && targetDay) {
    const source = parseInt(sourceDay) - 1;
    const target = parseInt(targetDay) - 1;
    editor.copyDay(source, target);
  }
}

// 导出JSON功能
function exportJSON() {
  if (!editor) {
    alert('编辑器未初始化');
    return;
  }
  
  editor.exportPlanAsJSON();
}

// 导入JSON功能
function importJSON() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = function(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const jsonData = e.target.result;
          if (editor) {
            editor.importPlanFromJSON(jsonData);
          }
        } catch (error) {
          alert('文件读取失败: ' + error.message);
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
}

function closeTemplateModal() {
  document.getElementById('templateModal').style.display = 'none';
}

async function selectTemplate(templateName) {
  if (editor) {
    await editor.changeMode(templateName);
    closeTemplateModal();
    
    // 更新计划名称
    const planNameInput = document.getElementById('planName');
    if (planNameInput) {
      planNameInput.value = `我的${templateName}计划`;
    }
  }
}

function previewPlan() {

  if (!editor) {
    alert('编辑器未初始化，请刷新页面重试');
    return;
  }
  
  if (typeof editor.generatePreviewHTML !== 'function') {
    console.error('generatePreviewHTML method not found on editor:', editor);
    alert('预览功能暂时不可用，请稍后重试');
    return;
  }
  
  const planName = document.getElementById('planName').value.trim();
  if (!planName) {
    alert('请输入计划名称！');
    return;
  }
  
  try {
    const previewWindow = window.open('', '_blank', 'width=900,height=700,scrollbars=yes');
    const previewHTML = editor.generatePreviewHTML();
    
    previewWindow.document.open();
    previewWindow.document.write(previewHTML);
    previewWindow.document.close();
  } catch (error) {
    console.error('预览失败:', error);
    alert('预览失败: ' + error.message);
  }
}

function savePlan() {

  if (!editor) {
    alert('编辑器未初始化，请刷新页面重试');
    return;
  }
  if (editor) {
    const planName = document.getElementById('planName').value.trim();
    const cycleWeeks = document.getElementById('cycleWeeks').value;
    
    if (!planName) {
      alert('请输入计划名称！');
      return;
    }
    
    // 检查是否有训练内容
    const hasContent = editor.planData.week_schedule.some(day => 
      Object.values(day.modules).some(module => module.length > 0)
    );
    
    if (!hasContent) {
      alert('请至少添加一些训练动作！');
      return;
    }
    
    // 准备保存数据，转换格式以匹配API要求
    const saveData = {
      name: planName,
      mode: editor.planData.mode,
      cycle_weeks: parseInt(cycleWeeks),
      plan_id: editor.currentPlanId, // 如果有ID则更新现有计划
      week_schedule: editor.planData.week_schedule.map((day, index) => {
        // 提取所有动作到一个数组中
        const exercises = [];
        Object.keys(day.modules).forEach(moduleKey => {
          day.modules[moduleKey].forEach(exercise => {
            exercises.push({
              name: typeof exercise.name === 'string' ? exercise.name : (exercise.name?.name || exercise.name?.title || '未知动作'),
              sets: parseInt(exercise.sets) || 1,
              reps: exercise.reps || '',
              weight: exercise.weight || '',
              rest: exercise.rest || '',
              module: moduleKey
            });
          });
        });
        
        return {
          day: index + 1,
          name: day.weekday + ' ' + day.body_parts.join('+'),
          type: day.body_parts.join(','),
          exercises: exercises
        };
      }).filter(day => day.exercises.length > 0) // 只保存有内容的天
    };

    // 显示保存中状态
    editor.showNotification('正在保存训练计划...', 'info');
    
    // 获取CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;


    // 保存到服务器
    fetch('/tools/api/training_plans/editor/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken || ''
      },
      body: JSON.stringify(saveData)
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    }).then(data => {
      if (data && data.success) {
        editor.showNotification(`训练计划"${planName}"已保存！`, 'success');
        // 保存计划ID以便后续更新
        editor.currentPlanId = data.plan.id;
        
        // 同时保存到本地存储作为备份
        localStorage.setItem('training_plan_backup', JSON.stringify(editor.planData));
      } else {
        throw new Error(data.error || '保存失败');
      }
    }).catch(error => {
      console.error('保存失败:', error);
      // 保存到本地存储作为备份
      localStorage.setItem('training_plan', JSON.stringify(editor.planData));
      editor.showNotification(`保存失败：${error.message}，已保存到本地`, 'error');
    });
  }
}

function publishPlan() {
  if (editor) {
    const planName = document.getElementById('planName').value.trim();
    if (!planName) {
      alert('请先填写计划名称！');
      return;
    }
    
    // 检查是否有训练内容
    const hasContent = editor.planData.week_schedule.some(day => 
      Object.values(day.modules).some(module => module.length > 0)
    );
    
    if (!hasContent) {
      alert('请至少添加一些训练动作！');
      return;
    }
    
    editor.showNotification('发布功能开发中...', 'info');
  }
}

function copyDay() {
  if (editor) {
    editor.showNotification('复制功能开发中...', 'info');
  }
}

function clearDay() {
  if (editor) {
    if (confirm('确定要清空当前训练日的所有内容吗？')) {
      const currentDay = editor.planData.week_schedule[editor.currentDay];
      Object.keys(currentDay.modules).forEach(module => {
        currentDay.modules[module] = [];
      });
      Object.keys(currentDay.modules).forEach(module => {
        if (!editor.isDragging) {
          editor.renderModule(module, currentDay.modules[module]);
        }
      });
      editor.renderWeekCards();
      editor.showNotification('已清空当前训练日', 'info');
    }
  }
}

function manageWeights() {
  if (editor) {
    editor.showNotification('重量管理功能开发中...', 'info');
  }
}

function addExerciseToModule(module) {
  if (!editor) {
    alert('编辑器未初始化');
    return;
  }
  
  // 创建动作输入模态框
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.id = 'addExerciseModal';
  
  const moduleNames = {
    warmup: '热身',
    main: '主训',
    accessory: '辅助',
    cooldown: '拉伸'
  };
  
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3><i class="fas fa-plus"></i> 添加动作到${moduleNames[module]}模块</h3>
        <button class="modal-close" onclick="closeAddExerciseModal()">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body" style="padding: 20px;">
        <div class="form-group" style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px; font-weight: bold;">动作名称 *</label>
          <input type="text" id="exerciseName" placeholder="请输入动作名称，如：杠铃卧推" 
                 style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
          <div class="form-group">
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">组数</label>
            <input type="text" id="exerciseSets" value="${getDefaultSets(module)}" 
                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
          </div>
          <div class="form-group">
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">次数/时间</label>
            <input type="text" id="exerciseReps" value="${getDefaultReps(module)}" 
                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
          <div class="form-group">
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">重量(kg)</label>
            <input type="text" id="exerciseWeight" placeholder="选填，如：60或空杆" 
                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
          </div>
          <div class="form-group">
            <label style="display: block; margin-bottom: 5px; font-weight: bold;">休息时间</label>
            <input type="text" id="exerciseRest" value="${getDefaultRest(module)}" 
                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
          </div>
        </div>
        
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <button onclick="closeAddExerciseModal()" 
                  style="padding: 8px 16px; border: 1px solid #ddd; background: #f5f5f5; border-radius: 4px; cursor: pointer;">
            取消
          </button>
          <button onclick="confirmAddExercise('${module}')" 
                  style="padding: 8px 16px; border: none; background: #4CAF50; color: white; border-radius: 4px; cursor: pointer;">
            <i class="fas fa-plus"></i> 添加动作
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // 焦点到名称输入框
  setTimeout(() => {
    document.getElementById('exerciseName').focus();
  }, 100);
  
  // 支持回车键确认
  document.getElementById('exerciseName').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      confirmAddExercise(module);
    }
  });
}

// 获取模块默认参数的辅助函数
function getDefaultSets(module) {
  const defaults = {
    warmup: '2',
    main: '4', 
    accessory: '3',
    cooldown: '1'
  };
  return defaults[module] || '3';
}

function getDefaultReps(module) {
  const defaults = {
    warmup: '15-20',
    main: '8-10',
    accessory: '10-12', 
    cooldown: '10分钟'
  };
  return defaults[module] || '10-12';
}

function getDefaultRest(module) {
  const defaults = {
    warmup: '30秒',
    main: '3分钟',
    accessory: '90秒',
    cooldown: '无'
  };
  return defaults[module] || '90秒';
}

// 确认添加动作
function confirmAddExercise(module) {
  const exerciseName = document.getElementById('exerciseName').value.trim();
  const exerciseSets = document.getElementById('exerciseSets').value.trim();
  const exerciseReps = document.getElementById('exerciseReps').value.trim();
  const exerciseWeight = document.getElementById('exerciseWeight').value.trim();
  const exerciseRest = document.getElementById('exerciseRest').value.trim();
  
  if (!exerciseName) {
    alert('请输入动作名称');
    document.getElementById('exerciseName').focus();
    return;
  }
  
  // 创建动作对象
  const exercise = {
    name: exerciseName,
    sets: exerciseSets || '3',
    reps: exerciseReps || '10-12', 
    weight: exerciseWeight || '',
    rest: exerciseRest || '90秒'
  };
  
  // 添加到编辑器
  if (editor) {
    const currentDay = editor.planData.week_schedule[editor.currentDay];
    currentDay.modules[module].push(exercise);
    if (!editor.isDragging) {
      editor.renderModule(module, currentDay.modules[module]);
    }
    editor.renderWeekCards();
    
    const moduleNames = {
      warmup: '热身',
      main: '主训', 
      accessory: '辅助',
      cooldown: '拉伸'
    };
    
    editor.showNotification(`已添加"${exerciseName}"到${moduleNames[module]}模块`, 'success');
  }
  
  // 关闭模态框
  closeAddExerciseModal();
}

// 关闭添加动作模态框
function closeAddExerciseModal() {
  const modal = document.getElementById('addExerciseModal');
  if (modal) {
    modal.remove();
  }
}



function searchExercises() {
  const searchInput = document.getElementById('exerciseSearch');
  if (!searchInput) return;
  
  const searchTerm = (searchInput.value || '').toLowerCase();
  const exerciseItems = document.querySelectorAll('.exercise-item');
  
  exerciseItems.forEach(item => {
    const nameElement = item.querySelector('span');
    if (!nameElement) return;
    
    const exerciseName = (nameElement.textContent || '').toLowerCase();
    if (exerciseName.includes(searchTerm)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

// 全局备用函数
function showWeekSettings() {

  if (window.editor && typeof window.editor.showWeekSettings === 'function') {
    window.editor.showWeekSettings();
  } else {
    alert('周安排设置功能开发中...');
  }
}

// 初始化编辑器
let editor;
document.addEventListener('DOMContentLoaded', function() {
  try {

    editor = new TrainingPlanEditor();

    // 验证全局函数是否正确定义





    // 页面加载完成后显示内容
    const container = document.querySelector('.plan-editor-container');
    if (container) {
      container.style.opacity = '1';
    }
  } catch (error) {
    console.error('训练计划编辑器初始化失败:', error);
    // 显示错误信息给用户
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #f44336;
      color: white;
      padding: 20px;
      border-radius: 8px;
      z-index: 10000;
      text-align: center;
    `;
    errorDiv.innerHTML = `
      <h3>页面加载失败</h3>
      <p>训练计划编辑器初始化失败，请刷新页面重试</p>
      <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 4px; background: white; color: #f44336; cursor: pointer;">刷新页面</button>
    `;
    document.body.appendChild(errorDiv);
  }
});
