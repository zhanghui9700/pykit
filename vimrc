" Pathogen
execute pathogen#infect()
call pathogen#helptags() " generate helptags for everything in 'runtimepath'
filetype plugin indent on

syntax on
set tabstop=4
set softtabstop=4
set shiftwidth=4
set nu
set autoindent
set smartindent
set expandtab
set mouse=nv
set cursorline

set list
set listchars=tab:>-,trail:<

autocmd FileType c set expandtab
autocmd FileType python set expandtab

set hlsearch
hi Search guibg=LightBlue

au BufReadPost * if line("'\"") > 0|if line("'\"") <= line("$")|exe("norm '\"")|else|exe "norm $"|endif|endif

set guifont=Bitstream_Vera_Sans_Mono:h12:cANSI
set background=dark
colorscheme solarized
colorscheme peachpuff
highlight Comment ctermfg=green guifg=green
set statusline=[%n]\ %f%m%r%h\ %=\|\ %l,%c\ %p%%\ \|\ %{((&fenc==\"\")?\"\":\"\ \".&fenc)}\ \|\ %{hostname()}

let g:pep8_map='<F8>'
