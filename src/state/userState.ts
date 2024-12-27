import { atom } from "recoil";
import { SET_NOTE, SET_SEARCH_NOTE, SET_STOCK_NOTE } from "util/actionTypes";

export const userState = atom({
  key: 'userState',
  default: {
    stockNote: [],
    userNote: [],
    searchedNote: []
  },
});
export const manageUserState = (actionType: string, payload: any, setState: Function, state: any) => {
  switch (actionType) {
    case SET_NOTE:
      setState({
        ...state,
        stockNote: [
          payload.data,
          ...state.stockNote
        ],
        userNote: [
          ...state.stockNote,
          payload.data
        ],
      });
      break;
    case SET_STOCK_NOTE:
      setState({
        ...state,
        stockNote: payload.data,
      });
      break;
    case SET_SEARCH_NOTE:
      setState({
        ...state,
        searchedNote: payload.data,
      });
      break;
    default:
      break;
  }
}