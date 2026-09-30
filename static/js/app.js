function confirmDelete(){return confirm('Are you sure you want to delete this item?');}

const root=document.documentElement;
const menu=document.getElementById('menuToggle');
const sidebar=document.getElementById('sidebar');
const scrim=document.getElementById('sidebarScrim');
const themeToggle=document.getElementById('themeToggle');

function closeMenu(){sidebar?.classList.remove('is-open');scrim?.classList.remove('is-open');document.body.classList.remove('menu-open')}
menu?.addEventListener('click',()=>{sidebar?.classList.add('is-open');scrim?.classList.add('is-open');document.body.classList.add('menu-open')});
scrim?.addEventListener('click',closeMenu);
document.querySelector('.sidebar-close')?.addEventListener('click',closeMenu);

function cssColor(name){return getComputedStyle(root).getPropertyValue(name).trim()}
function applyChartTheme(){
  if(!window.Chart)return;
  const muted=cssColor('--muted'),grid=cssColor('--chart-grid'),surface=cssColor('--tooltip'),text=cssColor('--text');
  Chart.defaults.color=muted;Chart.defaults.borderColor=grid;Chart.defaults.font.family='Inter, sans-serif';
  Chart.defaults.plugins.tooltip.backgroundColor=surface;Chart.defaults.plugins.tooltip.titleColor=text;Chart.defaults.plugins.tooltip.bodyColor=muted;Chart.defaults.plugins.tooltip.padding=12;Chart.defaults.plugins.tooltip.cornerRadius=6;
  Object.values(Chart.instances||{}).forEach(chart=>{
    if(chart.options?.plugins?.legend?.labels)chart.options.plugins.legend.labels.color=muted;
    Object.values(chart.options?.scales||{}).forEach(scale=>{if(scale.ticks)scale.ticks.color=muted;if(scale.grid)scale.grid.color=grid});
    chart.update('none');
  });
}
function setTheme(theme){root.dataset.theme=theme;localStorage.setItem('cadence-theme',theme);themeToggle?.setAttribute('aria-label',theme==='dark'?'Switch to light mode':'Switch to dark mode');themeToggle?.setAttribute('title',theme==='dark'?'Switch to light mode':'Switch to dark mode');applyChartTheme();window.dispatchEvent(new CustomEvent('cadence-theme-change',{detail:{theme}}))}
themeToggle?.addEventListener('click',()=>setTheme(root.dataset.theme==='dark'?'light':'dark'));
setTheme(root.dataset.theme||'dark');
