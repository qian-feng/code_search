if( NOT LLVM_REQUIRES_RTTI )
  if( NOT LLVM_REQUIRES_EH )
    set(LLVM_EXPORTED_SYMBOL_FILE ${CMAKE_CURRENT_SOURCE_DIR}/Hello0.exports)
  endif()
endif()

if(WIN32 OR CYGWIN)
  set(LLVM_LINK_COMPONENTS core Support)
endif()
add_library(igraph STATIC IMPORTED)
include_directories(/home/qian/res)
add_library(LLVMHello0 MODULE Hello0.cpp)
set_target_properties( igraph PROPERTIES IMPORTED_LOCATION /home/qian/res/libigraph.so )
target_link_libraries(LLVMHello0 igraph)

