"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[495],{3695:(e,t,r)=>{r.d(t,{AM:()=>l,Wv:()=>i,hl:()=>d});var n=r(1074),a=r(44576),o=r(17178),s=r(78388);let l=a.bL,i=a.l9,d=o.forwardRef((e,t)=>{let{className:r,align:o="center",sideOffset:l=4,...i}=e;return(0,n.jsx)(a.ZL,{children:(0,n.jsx)(a.UC,{ref:t,align:o,sideOffset:l,side:"bottom",className:(0,s.QP)("z-50 min-w-[220px] max-w-[98vw] rounded-lg border bg-fd-popover p-2 text-sm text-fd-popover-foreground shadow-md focus-visible:outline-none data-[state=closed]:animate-fd-popover-out data-[state=open]:animate-fd-popover-in",r),...i})})});d.displayName=a.UC.displayName,a.iN},19683:(e,t,r)=>{r.d(t,{NavProvider:()=>d,Title:()=>u,h:()=>c});var n=r(1074),a=r(68313),o=r(17178),s=r(78388),l=r(40627);let i=(0,o.createContext)({isTransparent:!1});function d(e){let{transparentMode:t="none",children:r}=e,[a,s]=(0,o.useState)("none"!==t);return(0,o.useEffect)(()=>{if("top"!==t)return;let e=()=>{s(window.scrollY<10)};return e(),window.addEventListener("scroll",e),()=>{window.removeEventListener("scroll",e)}},[t]),(0,n.jsx)(i.Provider,{value:{isTransparent:a},children:r})}function c(){return(0,o.useContext)(i)}function u(e){let{title:t,url:r,...o}=e,{locale:i}=(0,l.s9)();return(0,n.jsx)(a.A,{href:null!=r?r:i?"/".concat(i):"/",...o,className:(0,s.QP)("inline-flex items-center gap-2.5 font-semibold",o.className),children:t})}},20973:(e,t,r)=>{r.d(t,{$:()=>n});function n(e,t,r=!0){return e.endsWith("/")&&(e=e.slice(0,-1)),t.endsWith("/")&&(t=t.slice(0,-1)),e===t||r&&t.startsWith(`${e}/`)}},40627:(e,t,r)=>{r.d(t,{I18nLabel:()=>o,s9:()=>s});var n=r(17178);let a=(0,n.createContext)({text:{search:"Search",searchNoResult:"No results found",toc:"On this page",tocNoHeadings:"No Headings",lastUpdate:"Last updated on",chooseLanguage:"Choose a language",nextPage:"Next",previousPage:"Previous",chooseTheme:"Theme",editOnGithub:"Edit on GitHub"}});function o(e){let{text:t}=s();return t[e.label]}function s(){return(0,n.useContext)(a)}},44576:(e,t,r)=>{r.d(t,{UC:()=>Z,ZL:()=>U,bL:()=>H,i3:()=>$,iN:()=>z,l9:()=>q});var n=r(17178),a=r(80828),o=r(97571),s=r(14553),l=r(15946),i=r(55891),d=r(24076),c=r(37134),u=r(17654),h=r(45522),m=r(89892),p=r(73090),f=r(1118),v=r(56542),g=r(16732),x=r(20166),y=r(1074),b="Popover",[k,w]=(0,s.A)(b,[u.Bk]),C=(0,u.Bk)(),[P,j]=k(b),N=e=>{let{__scopePopover:t,children:r,open:a,defaultOpen:o,onOpenChange:s,modal:l=!1}=e,i=C(t),d=n.useRef(null),[h,m]=n.useState(!1),[p=!1,f]=(0,v.i)({prop:a,defaultProp:o,onChange:s});return(0,y.jsx)(u.bL,{...i,children:(0,y.jsx)(P,{scope:t,contentId:(0,c.B)(),triggerRef:d,open:p,onOpenChange:f,onOpenToggle:n.useCallback(()=>f(e=>!e),[f]),hasCustomAnchor:h,onCustomAnchorAdd:n.useCallback(()=>m(!0),[]),onCustomAnchorRemove:n.useCallback(()=>m(!1),[]),modal:l,children:r})})};N.displayName=b;var A="PopoverAnchor";n.forwardRef((e,t)=>{let{__scopePopover:r,...a}=e,o=j(A,r),s=C(r),{onCustomAnchorAdd:l,onCustomAnchorRemove:i}=o;return n.useEffect(()=>(l(),()=>i()),[l,i]),(0,y.jsx)(u.Mz,{...s,...a,ref:t})}).displayName=A;var E="PopoverTrigger",S=n.forwardRef((e,t)=>{let{__scopePopover:r,...n}=e,s=j(E,r),l=C(r),i=(0,o.s)(t,s.triggerRef),d=(0,y.jsx)(p.sG.button,{type:"button","aria-haspopup":"dialog","aria-expanded":s.open,"aria-controls":s.contentId,"data-state":K(s.open),...n,ref:i,onClick:(0,a.m)(e.onClick,s.onOpenToggle)});return s.hasCustomAnchor?d:(0,y.jsx)(u.Mz,{asChild:!0,...l,children:d})});S.displayName=E;var L="PopoverPortal",[T,R]=k(L,{forceMount:void 0}),O=e=>{let{__scopePopover:t,forceMount:r,children:n,container:a}=e,o=j(L,t);return(0,y.jsx)(T,{scope:t,forceMount:r,children:(0,y.jsx)(m.C,{present:r||o.open,children:(0,y.jsx)(h.Z,{asChild:!0,container:a,children:n})})})};O.displayName=L;var M="PopoverContent",_=n.forwardRef((e,t)=>{let r=R(M,e.__scopePopover),{forceMount:n=r.forceMount,...a}=e,o=j(M,e.__scopePopover);return(0,y.jsx)(m.C,{present:n||o.open,children:o.modal?(0,y.jsx)(D,{...a,ref:t}):(0,y.jsx)(F,{...a,ref:t})})});_.displayName=M;var D=n.forwardRef((e,t)=>{let r=j(M,e.__scopePopover),s=n.useRef(null),l=(0,o.s)(t,s),i=n.useRef(!1);return n.useEffect(()=>{let e=s.current;if(e)return(0,g.Eq)(e)},[]),(0,y.jsx)(x.A,{as:f.DX,allowPinchZoom:!0,children:(0,y.jsx)(I,{...e,ref:l,trapFocus:r.open,disableOutsidePointerEvents:!0,onCloseAutoFocus:(0,a.m)(e.onCloseAutoFocus,e=>{var t;e.preventDefault(),i.current||null===(t=r.triggerRef.current)||void 0===t||t.focus()}),onPointerDownOutside:(0,a.m)(e.onPointerDownOutside,e=>{let t=e.detail.originalEvent,r=0===t.button&&!0===t.ctrlKey;i.current=2===t.button||r},{checkForDefaultPrevented:!1}),onFocusOutside:(0,a.m)(e.onFocusOutside,e=>e.preventDefault(),{checkForDefaultPrevented:!1})})})}),F=n.forwardRef((e,t)=>{let r=j(M,e.__scopePopover),a=n.useRef(!1),o=n.useRef(!1);return(0,y.jsx)(I,{...e,ref:t,trapFocus:!1,disableOutsidePointerEvents:!1,onCloseAutoFocus:t=>{var n,s;null===(n=e.onCloseAutoFocus)||void 0===n||n.call(e,t),t.defaultPrevented||(a.current||null===(s=r.triggerRef.current)||void 0===s||s.focus(),t.preventDefault()),a.current=!1,o.current=!1},onInteractOutside:t=>{var n,s;null===(n=e.onInteractOutside)||void 0===n||n.call(e,t),t.defaultPrevented||(a.current=!0,"pointerdown"!==t.detail.originalEvent.type||(o.current=!0));let l=t.target;(null===(s=r.triggerRef.current)||void 0===s?void 0:s.contains(l))&&t.preventDefault(),"focusin"===t.detail.originalEvent.type&&o.current&&t.preventDefault()}})}),I=n.forwardRef((e,t)=>{let{__scopePopover:r,trapFocus:n,onOpenAutoFocus:a,onCloseAutoFocus:o,disableOutsidePointerEvents:s,onEscapeKeyDown:c,onPointerDownOutside:h,onFocusOutside:m,onInteractOutside:p,...f}=e,v=j(M,r),g=C(r);return(0,i.Oh)(),(0,y.jsx)(d.n,{asChild:!0,loop:!0,trapped:n,onMountAutoFocus:a,onUnmountAutoFocus:o,children:(0,y.jsx)(l.qW,{asChild:!0,disableOutsidePointerEvents:s,onInteractOutside:p,onEscapeKeyDown:c,onPointerDownOutside:h,onFocusOutside:m,onDismiss:()=>v.onOpenChange(!1),children:(0,y.jsx)(u.UC,{"data-state":K(v.open),role:"dialog",id:v.contentId,...g,...f,ref:t,style:{...f.style,"--radix-popover-content-transform-origin":"var(--radix-popper-transform-origin)","--radix-popover-content-available-width":"var(--radix-popper-available-width)","--radix-popover-content-available-height":"var(--radix-popper-available-height)","--radix-popover-trigger-width":"var(--radix-popper-anchor-width)","--radix-popover-trigger-height":"var(--radix-popper-anchor-height)"}})})})}),W="PopoverClose",z=n.forwardRef((e,t)=>{let{__scopePopover:r,...n}=e,o=j(W,r);return(0,y.jsx)(p.sG.button,{type:"button",...n,ref:t,onClick:(0,a.m)(e.onClick,()=>o.onOpenChange(!1))})});z.displayName=W;var Q=n.forwardRef((e,t)=>{let{__scopePopover:r,...n}=e,a=C(r);return(0,y.jsx)(u.i3,{...a,...n,ref:t})});function K(e){return e?"open":"closed"}Q.displayName="PopoverArrow";var H=N,q=S,U=O,Z=_,$=Q},46179:(e,t,r)=>{r.r(t),r.d(t,{BaseLinkItem:()=>i});var n=r(1074),a=r(68313),o=r(85632),s=r(17178),l=r(20973);let i=(0,s.forwardRef)((e,t)=>{var r;let{item:s,...i}=e,d=(0,o.usePathname)(),c=null!==(r=s.active)&&void 0!==r?r:"url",u="none"!==c&&(0,l.$)(s.url,d,"nested-url"===c);return(0,n.jsx)(a.A,{ref:t,href:s.url,external:s.external,...i,"data-active":u,children:i.children})});i.displayName="BaseLinkItem"},52289:(e,t,r)=>{r.d(t,{ThemeToggle:()=>m});var n=r(1074),a=r(1145),o=r(66378);let s=(0,o.A)("Sun",[["circle",{cx:"12",cy:"12",r:"4",key:"4exip2"}],["path",{d:"M12 2v2",key:"tus03m"}],["path",{d:"M12 20v2",key:"1lh1kg"}],["path",{d:"m4.93 4.93 1.41 1.41",key:"149t6j"}],["path",{d:"m17.66 17.66 1.41 1.41",key:"ptbguv"}],["path",{d:"M2 12h2",key:"1t8f8n"}],["path",{d:"M20 12h2",key:"1q8mjw"}],["path",{d:"m6.34 17.66-1.41 1.41",key:"1m8zz5"}],["path",{d:"m19.07 4.93-1.41 1.41",key:"1shlcs"}]]),l=(0,o.A)("Moon",[["path",{d:"M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z",key:"a7tn18"}]]),i=(0,o.A)("Airplay",[["path",{d:"M5 17H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-1",key:"ns4c3b"}],["path",{d:"m12 15 5 6H7Z",key:"14qnn2"}]]);var d=r(99005),c=r(17178),u=r(78388);let h=(0,a.F)("size-7 rounded-full p-1.5 text-fd-muted-foreground",{variants:{active:{true:"bg-fd-accent text-fd-accent-foreground",false:"text-fd-muted-foreground"}}});function m(e){let{className:t,mode:r="light-dark",...a}=e,{setTheme:o,theme:m,resolvedTheme:p}=(0,d.D)(),[f,v]=(0,c.useState)(!1);(0,c.useLayoutEffect)(()=>{v(!0)},[]);let g=(0,u.QP)("inline-flex items-center rounded-full border p-[3px]",t);if("light-dark"===r){let e=f?p:null;return(0,n.jsxs)("button",{className:g,onClick:()=>o("light"===e?"dark":"light"),"data-theme-toggle":"",...a,children:[(0,n.jsx)(s,{className:(0,u.QP)(h({active:"light"===e}))}),(0,n.jsx)(l,{className:(0,u.QP)(h({active:"dark"===e}))})]})}let x=f?m:null;return(0,n.jsx)("div",{className:g,"data-theme-toggle":"",...a,children:[["light",s],["dark",l],["system",i]].map(e=>{let[t,r]=e;return(0,n.jsx)("button",{"aria-label":t,className:(0,u.QP)(h({active:x===t})),onClick:()=>o(t),children:(0,n.jsx)(r,{className:"size-full"})},t)})})}},56337:(e,t,r)=>{r.d(t,{LargeSearchToggle:()=>c,SearchToggle:()=>d});var n=r(1074),a=r(65313),o=r(76955),s=r(40627),l=r(78388),i=r(27802);function d(e){let{hideIfDisabled:t,...r}=e,{setOpenSearch:s,enabled:d}=(0,o.$A)();return t&&!d?null:(0,n.jsx)("button",{type:"button",className:(0,l.QP)((0,i.r)({size:"icon",color:"ghost"}),r.className),"data-search":"","aria-label":"Open Search",onClick:()=>{s(!0)},children:(0,n.jsx)(a.A,{})})}function c(e){let{hideIfDisabled:t,...r}=e,{enabled:i,hotKey:d,setOpenSearch:c}=(0,o.$A)(),{text:u}=(0,s.s9)();return t&&!i?null:(0,n.jsxs)("button",{type:"button","data-search-full":"",...r,className:(0,l.QP)("inline-flex items-center gap-2 rounded-full border bg-fd-secondary/50 p-1.5 text-sm text-fd-muted-foreground transition-colors hover:bg-fd-accent hover:text-fd-accent-foreground",r.className),onClick:()=>{c(!0)},children:[(0,n.jsx)(a.A,{className:"ms-1 size-4"}),u.search,(0,n.jsx)("div",{className:"ms-auto inline-flex gap-0.5",children:d.map((e,t)=>(0,n.jsx)("kbd",{className:"rounded-md border bg-fd-background px-1.5",children:e.display},t))})]})}},65313:(e,t,r)=>{r.d(t,{A:()=>n});let n=(0,r(66378).A)("Search",[["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}],["path",{d:"m21 21-4.3-4.3",key:"1qie3q"}]])},66435:(e,t,r)=>{},68313:(e,t,r)=>{r.d(t,{A:()=>s});var n=r(44063),a=r(17178),o=r(1074),s=(0,a.forwardRef)(({href:e="#",external:t=!(e.startsWith("/")||e.startsWith("#")||e.startsWith(".")),prefetch:r,replace:a,...s},l)=>t?(0,o.jsx)("a",{ref:l,href:e,rel:"noreferrer noopener",target:"_blank",...s,children:s.children}):(0,o.jsx)(n,{ref:l,href:e,prefetch:r,replace:a,...s}));s.displayName="Link",r(66435)},76955:(e,t,r)=>{r.d(t,{$A:()=>s,YL:()=>i});var n=r(1074),a=r(17178);let o=(0,a.createContext)({enabled:!1,hotKey:[],setOpenSearch:()=>void 0});function s(){return(0,a.useContext)(o)}function l(){let[e,t]=(0,a.useState)("⌘");return(0,a.useEffect)(()=>{window.navigator.userAgent.includes("Windows")&&t("Ctrl")},[]),e}function i(e){let{SearchDialog:t,children:r,preload:s=!0,options:i,hotKey:d=[{key:e=>e.metaKey||e.ctrlKey,display:(0,n.jsx)(l,{})},{key:"k",display:"K"}],links:c}=e,[u,h]=(0,a.useState)(!s&&void 0);return(0,a.useEffect)(()=>{let e=e=>{d.every(t=>"string"==typeof t.key?e.key===t.key:t.key(e))&&(h(!0),e.preventDefault())};return window.addEventListener("keydown",e),()=>{window.removeEventListener("keydown",e)}},[d]),(0,n.jsxs)(o.Provider,{value:(0,a.useMemo)(()=>({enabled:!0,hotKey:d,setOpenSearch:h}),[d]),children:[void 0!==u&&(0,n.jsx)(t,{open:u,onOpenChange:h,links:c,...i}),r]})}},80923:(e,t,r)=>{r.d(t,{LanguageToggle:()=>i,LanguageToggleText:()=>d});var n=r(1074),a=r(40627),o=r(3695),s=r(78388),l=r(27802);function i(e){let t=(0,a.s9)();if(!t.locales)throw Error("Missing `<I18nProvider />`");return(0,n.jsxs)(o.AM,{children:[(0,n.jsx)(o.Wv,{"aria-label":t.text.chooseLanguage,...e,className:(0,s.QP)((0,l.r)({color:"ghost",className:"gap-1.5 p-1.5"}),e.className),children:e.children}),(0,n.jsxs)(o.hl,{className:"flex flex-col overflow-hidden p-0",children:[(0,n.jsx)("p",{className:"mb-1 p-2 text-xs font-medium text-fd-muted-foreground",children:t.text.chooseLanguage}),t.locales.map(e=>(0,n.jsx)("button",{type:"button",className:(0,s.QP)("p-2 text-start text-sm",e.locale===t.locale?"bg-fd-primary/10 font-medium text-fd-primary":"hover:bg-fd-accent hover:text-fd-accent-foreground"),onClick:()=>{var r;null===(r=t.onChange)||void 0===r||r.call(t,e.locale)},children:e.name},e.locale))]})]})}function d(e){var t,r;let o=(0,a.s9)(),s=null===(r=o.locales)||void 0===r?void 0:null===(t=r.find(e=>e.locale===o.locale))||void 0===t?void 0:t.name;return(0,n.jsx)("span",{...e,children:s})}},85632:(e,t,r)=>{var n=r(60816);r.o(n,"useParams")&&r.d(t,{useParams:function(){return n.useParams}}),r.o(n,"usePathname")&&r.d(t,{usePathname:function(){return n.usePathname}}),r.o(n,"useRouter")&&r.d(t,{useRouter:function(){return n.useRouter}}),r.o(n,"useSearchParams")&&r.d(t,{useSearchParams:function(){return n.useSearchParams}})},99005:(e,t,r)=>{r.d(t,{D:()=>c,N:()=>u});var n=r(17178),a=(e,t,r,n,a,o,s,l)=>{let i=document.documentElement,d=["light","dark"];function c(t){var r;(Array.isArray(e)?e:[e]).forEach(e=>{let r="class"===e,n=r&&o?a.map(e=>o[e]||e):a;r?(i.classList.remove(...n),i.classList.add(o[t]||t)):i.setAttribute(e,t)}),r=t,l&&d.includes(r)&&(i.style.colorScheme=r)}if(n)c(n);else try{let e=localStorage.getItem(t)||r,n=s&&"system"===e?window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light":e;c(n)}catch(e){}},o=["light","dark"],s="(prefers-color-scheme: dark)",l="undefined"==typeof window,i=n.createContext(void 0),d={setTheme:e=>{},themes:[]},c=()=>{var e;return null!=(e=n.useContext(i))?e:d},u=e=>n.useContext(i)?n.createElement(n.Fragment,null,e.children):n.createElement(m,{...e}),h=["light","dark"],m=e=>{let{forcedTheme:t,disableTransitionOnChange:r=!1,enableSystem:a=!0,enableColorScheme:l=!0,storageKey:d="theme",themes:c=h,defaultTheme:u=a?"system":"light",attribute:m="data-theme",value:x,children:y,nonce:b,scriptProps:k}=e,[w,C]=n.useState(()=>f(d,u)),[P,j]=n.useState(()=>"system"===w?g():w),N=x?Object.values(x):c,A=n.useCallback(e=>{let t=e;if(!t)return;"system"===e&&a&&(t=g());let n=x?x[t]:t,s=r?v(b):null,i=document.documentElement,d=e=>{"class"===e?(i.classList.remove(...N),n&&i.classList.add(n)):e.startsWith("data-")&&(n?i.setAttribute(e,n):i.removeAttribute(e))};if(Array.isArray(m)?m.forEach(d):d(m),l){let e=o.includes(u)?u:null,r=o.includes(t)?t:e;i.style.colorScheme=r}null==s||s()},[b]),E=n.useCallback(e=>{let t="function"==typeof e?e(w):e;C(t);try{localStorage.setItem(d,t)}catch(e){}},[w]),S=n.useCallback(e=>{j(g(e)),"system"===w&&a&&!t&&A("system")},[w,t]);n.useEffect(()=>{let e=window.matchMedia(s);return e.addListener(S),S(e),()=>e.removeListener(S)},[S]),n.useEffect(()=>{let e=e=>{e.key===d&&(e.newValue?C(e.newValue):E(u))};return window.addEventListener("storage",e),()=>window.removeEventListener("storage",e)},[E]),n.useEffect(()=>{A(null!=t?t:w)},[t,w]);let L=n.useMemo(()=>({theme:w,setTheme:E,forcedTheme:t,resolvedTheme:"system"===w?P:w,themes:a?[...c,"system"]:c,systemTheme:a?P:void 0}),[w,E,t,P,a,c]);return n.createElement(i.Provider,{value:L},n.createElement(p,{forcedTheme:t,storageKey:d,attribute:m,enableSystem:a,enableColorScheme:l,defaultTheme:u,value:x,themes:c,nonce:b,scriptProps:k}),y)},p=n.memo(e=>{let{forcedTheme:t,storageKey:r,attribute:o,enableSystem:s,enableColorScheme:l,defaultTheme:i,value:d,themes:c,nonce:u,scriptProps:h}=e,m=JSON.stringify([o,r,i,t,c,d,s,l]).slice(1,-1);return n.createElement("script",{...h,suppressHydrationWarning:!0,nonce:"undefined"==typeof window?u:"",dangerouslySetInnerHTML:{__html:"(".concat(a.toString(),")(").concat(m,")")}})}),f=(e,t)=>{let r;if(!l){try{r=localStorage.getItem(e)||void 0}catch(e){}return r||t}},v=e=>{let t=document.createElement("style");return e&&t.setAttribute("nonce",e),t.appendChild(document.createTextNode("*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}")),document.head.appendChild(t),()=>{window.getComputedStyle(document.body),setTimeout(()=>{document.head.removeChild(t)},1)}},g=e=>(e||(e=window.matchMedia(s)),e.matches?"dark":"light")}}]);